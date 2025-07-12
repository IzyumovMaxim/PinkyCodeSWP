## Acceptance Tests
1) Open the login page, enter login and password, click Log in, and confirm you are on the main page.
2) From the main page, upload .zip, download the .csv file and confirm the comments have been correctly assessed.
3) Click Log out, then reopen the app’s base URL and confirm you see starting page with the login button.
4) From main page go to admin page and Verify that when the administrator clicks the “Add TA” button on their profile and submits valid details, the new TA is created in the system and appears in the TA list.

## Corresponding Acceptance Criteria
1) Given: user open login page, when he enters his personal information, then he enters the main page.
2) Given the current prompt. When the user submits the file, they will get well-structured feedback without hallucinations from LLM.
3) Given: the customer's code, when the code is uploaded, then all meaningless comments are assessed.
4) Given: the admin's profile, when he click on "add TA" button, new TA will be added to the system