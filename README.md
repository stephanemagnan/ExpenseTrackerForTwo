# ExpenseTracker
Expense tracking app for two people to track their expenses, split costs, and manage money together. Password protected accounts can be added to the account. 
 
## Technical details
A user profile contains data for purchases from two people forming the couple. Couples can add an unlimited number of different categories for their expenses (e.g., food, pharmacy, car, clothes, etc.), different payment methods (e.g., credit card, debit card, chequings account, etc.), and purchases that can be read in from a creadit card statement. Each payment is assigned to a category and payment details are added. You can also add details for how the cost will be shared (100%/0%, 50%/50%, 0%/100%, or any custom split). Based on all costs incurred by each couple, one or both individuals can pay their tab by transfering any outstanding balance to the other person or to a shared account. Tabs (or transfers) are also tracked within the database. 

## Implementation
The python project is intended to be a locally-hosted tool for managing expenses imported into a databse with tools for reporting and ensuring everyone contributes fairly. The project uses SQLAlchemy and Flask to handle user inputs in the browser.

## Getting Started
Navigate to the ExpenseTrackerForTwo folder in the IDE of your choice. Run the project to start the process in your default browser.

## References
Certain aspects of this project were inspired by a series of videos by Corey Shafer - https://www.youtube.com/watch?v=MwZwr5Tvyxo
