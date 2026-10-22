Prompts to Test Each Capability
Here is a progression of prompts to test the tool-calling behavior in your terminal:

1. Populate the Ledger (write operations)
"Log an expense of 450 INR for Groceries."

"Add an expense of 120 EUR under Hotel."

"Record 80 EUR for Dinner in the Food category."

2. Query the Ledger (read operations with get_expenses)
List everything:"Can you show me all my recorded expenses so far?"

Filter by category:"How much have I spent on Food?"

Filter by currency:"Show me all the expenses I paid in EUR."

3. Chained / Multi-tool reasoning
Read + Currency Conversion:"What is the total of my EUR expenses, and how much is that in INR?" (The assistant should retrieve the expenses, then use convert_currency for the amount.)

Read + Bill Split:"Look up my Hotel expense and tell me how much each person pays if we split it between 3 people."