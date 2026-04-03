from fastmcp import FastMCP
import httpx

# Initialize the MCP server
app = FastMCP("FinanceManager")

# Base URL for your Spring Boot service
BASE_URL = "http://localhost:8080"

# Global variable to store the JWT token
AUTH_TOKEN = None

@app.tool()
async def register(username: str, email: str, password: str, role: str = "USER") -> str:
    """Registers a new user and logs them in."""
    global AUTH_TOKEN
    async with httpx.AsyncClient() as client:
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        res = await client.post(f"{BASE_URL}/api/auth/register", json=payload)
        if res.status_code == 200:
            AUTH_TOKEN = res.json().get("token")
            return "Registration successful and logged in."
        else:
            return f"Registration failed: {res.text}"


@app.tool()
async def login(username: str, password: str) -> str:
    """Logs in a user and stores the authentication token."""
    global AUTH_TOKEN
    async with httpx.AsyncClient() as client:
        payload = {
            "username": username,
            "password": password
        }
        res = await client.post(f"{BASE_URL}/api/auth/authenticate", json=payload)
        if res.status_code == 200:
            AUTH_TOKEN = res.json().get("token")
            return "Login successful."
        else:
            return f"Login failed: {res.text}"

@app.tool()
async def logout() -> str:
    """Logs out the current user."""
    global AUTH_TOKEN
    AUTH_TOKEN = None
    return "Logout successful."


@app.tool()
async def get_all_transactions() -> str:
    """Fetch all transactions from the personal finance service."""
    if not AUTH_TOKEN:
        return "You must be logged in to perform this action. Use the 'login' tool."
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.get(f"{BASE_URL}/api/transactions")
        res.raise_for_status()  # Raise an exception for bad status codes
        data = res.json()

        # Format as a Markdown Table
        table = "| ID | Date | Description | Amount | Category |\n|---|---|---|---|---|"
        for t in data:
            category_name = t.get('category', {}).get('name', 'N/A') if t.get('category') else 'N/A'
            table += f"\n| {t.get('id')} | {t.get('date')} | {t.get('description')} | {t.get('amount')} | {category_name} |"
        return table

@app.tool()
async def get_all_categories() -> str:
    """Fetch all categories from the personal finance service."""
    if not AUTH_TOKEN:
        return "You must be logged in to perform this action. Use the 'login' tool."
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.get(f"{BASE_URL}/api/categories")
        res.raise_for_status()
        data = res.json()

        # Format as a Markdown Table
        table = "| ID | Name |\n|---|---|"
        for c in data:
            table += f"\n| {c.get('id')} | {c.get('name')} |"
        return table

@app.tool()
async def add_transaction(date: str, description: str, amount: float, category_name: str) -> str:
    """Adds a new transaction."""
    if not AUTH_TOKEN:
        return "You must be logged in to perform this action. Use the 'login' tool."
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    async with httpx.AsyncClient(headers=headers) as client:
        # Create or get category
        category_payload = {"name": category_name}
        try:
            res = await client.post(f"{BASE_URL}/api/categories", json=category_payload)
            res.raise_for_status()
            category = res.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409: # Conflict
                res_get = await client.get(f"{BASE_URL}/api/categories")
                res_get.raise_for_status()
                categories = res_get.json()
                found_category = next((c for c in categories if c['name'] == category_name), None)
                if not found_category:
                    return f"Failed to create or find category: {category_name}"
                category = found_category
            else:
                raise e

        # Create transaction
        transaction_payload = {
            "date": date,
            "description": description,
            "amount": amount,
            "category": category
        }
        res = await client.post(f"{BASE_URL}/api/transactions", json=transaction_payload)
        res.raise_for_status()
        return "Transaction added successfully."

@app.tool()
async def update_transaction(transaction_id: int, date: str, description: str, amount: float, category_name: str) -> str:
    """Updates an existing transaction."""
    if not AUTH_TOKEN:
        return "You must be logged in to perform this action. Use the 'login' tool."
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    async with httpx.AsyncClient(headers=headers) as client:
        # Create or get category
        category_payload = {"name": category_name}
        try:
            res = await client.post(f"{BASE_URL}/api/categories", json=category_payload)
            res.raise_for_status()
            category = res.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409: # Conflict
                res_get = await client.get(f"{BASE_URL}/api/categories")
                res_get.raise_for_status()
                categories = res_get.json()
                found_category = next((c for c in categories if c['name'] == category_name), None)
                if not found_category:
                    return f"Failed to create or find category: {category_name}"
                category = found_category
            else:
                raise e

        # Update transaction
        transaction_payload = {
            "date": date,
            "description": description,
            "amount": amount,
            "category": category
        }
        res = await client.put(f"{BASE_URL}/api/transactions/{transaction_id}", json=transaction_payload)
        res.raise_for_status()
        return "Transaction updated successfully."

@app.tool()
async def delete_transaction(transaction_id: int) -> str:
    """Deletes a transaction."""
    if not AUTH_TOKEN:
        return "You must be logged in to perform this action. Use the 'login' tool."
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.delete(f"{BASE_URL}/api/transactions/{transaction_id}")
        res.raise_for_status()
        return "Transaction deleted successfully."

@app.tool()
async def delete_user(username: str) -> str:
    """Deletes a user."""
    if not AUTH_TOKEN:
        return "You must be logged in to perform this action. Use the 'login' tool."
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    async with httpx.AsyncClient(headers=headers) as client:
        res = await client.delete(f"{BASE_URL}/api/users/{username}")
        res.raise_for_status()
        return "User deleted successfully."

if __name__ == "__main__":
    #app.run(transport="http", host="127.0.0.1", port=8000, stateless=True)
    app.run()