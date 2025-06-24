# Study-Snap Project Roadmap

This document outlines the current state of the project and the necessary steps to achieve the desired features.

## Current Status

- **Project Structure**: The project is set up with separate `frontend` and `backend` directories, which is a good practice for maintaining a clean codebase.
- **Backend**: A Python backend is in place, likely using a framework like Flask or FastAPI, contained within an `app` directory. It uses a virtual environment for dependency management.
- **Frontend**: A frontend directory exists, ready for building the user interface.

## Next Steps

Here is a breakdown of the tasks required to complete the application:

### 1. Authentication (Frontend and Backend)

-   **Backend (In-Progress):**
    -   [ ] **User Model**: Define a `User` model with fields for username, email, and hashed password.
    -   [ ] **Database Setup**: Configure a database (e.g., PostgreSQL, SQLite) and an ORM (e.g., SQLAlchemy) to manage user data.
    -   [ ] **Authentication Endpoints**:
        -   `POST /register`: To create a new user account.
        -   `POST /login`: To authenticate a user and issue a token.
        -   `GET /me`: To retrieve the current user's information.
    -   [ ] **Password Hashing**: Use a library like `passlib` to securely hash and verify passwords.
    -   [ ] **Token-based Authentication**: Implement JWT (JSON Web Tokens) for securing endpoints.

-   **Frontend (To-Do):**
    -   [ ] **UI Components**: Create login and registration forms.
    -   [ ] **State Management**: Use a state management library (e.g., Redux, Context API) to handle user authentication state.
    -   [ ] **API Integration**: Connect the frontend forms to the backend authentication endpoints.
    -   [ ] **Protected Routes**: Implement logic to restrict access to certain pages to authenticated users.

### 2. User Sessions

-   [ ] **Token Storage**: Securely store JWTs on the client-side (e.g., in `localStorage` or `sessionStorage`).
-   [ ] **Token Refresh**: Implement a mechanism to refresh tokens to keep users logged in without compromising security.
-   [ ] **Logout**: Create a logout function to clear the user's session from the client-side.

### 3. S3 for File Storage

-   [ ] **AWS Setup**: Create an AWS account and an S3 bucket to store user-uploaded files.
-   [ ] **Backend Integration**:
    -   Use the `boto3` library in your Python backend to interact with S3.
    -   Create endpoints for uploading files to and retrieving files from S3.
    -   Implement authorization to ensure users can only access their own files.
-   [ ] **Frontend Integration**:
    -   Create a file upload component.
    -   Develop a view to display a list of uploaded files and allow users to view or download them.

### 4. Google Calendar Integration

-   [ ] **Google Cloud Platform Setup**:
    -   Create a new project on the Google Cloud Platform.
    -   Enable the Google Calendar API.
    -   Configure OAuth 2.0 credentials (client ID and client secret).
-   [ ] **Backend Integration**:
    -   Use the Google API Python Client to handle the OAuth 2.0 flow for authorization.
    -   Create endpoints to:
        -   Initiate the Google login process.
        -   Handle the OAuth callback.
        -   Create, read, and update calendar events.
-   [ ] **Frontend Integration**:
    -   Add a "Connect to Google Calendar" button.
    -   Create a calendar view to display events from the user's Google Calendar.

### 5. Hosting and Deployment

-   **Backend**:
    -   [ ] **Containerization**: Use Docker to containerize the backend application.
    -   [ ] **Hosting Provider**: Choose a hosting provider (e.g., AWS, Heroku, Vercel) and deploy the Docker container.
-   **Frontend**:
    -   [ ] **Build Process**: Set up a build process to create a production-ready version of the frontend.
    -   [ ] **Hosting**: Deploy the static frontend files to a service like Netlify, Vercel, or AWS S3/CloudFront.
-   **CI/CD**:
    -   [ ] **Set up a CI/CD pipeline** (e.g., using GitHub Actions) to automate testing and deployment.

### 6. Additional Features and Considerations

-   **Testing**:
    -   [ ] Write unit and integration tests for the backend.
    -   [ ] Implement end-to-end tests for the frontend.
-   **UI/UX**:
    -   [ ] Design a user-friendly and responsive interface.
    -   [ ] Consider adding a UI library like Material-UI or Tailwind CSS.
-   **Security**:
    -   [ ] Set up CORS (Cross-Origin Resource Sharing) on the backend.
    -   [ ] Protect against common vulnerabilities (e.g., XSS, CSRF).
-   **Logging and Monitoring**:
    -   [ ] Implement logging to track application behavior and errors.
    -   [ ] Set up monitoring to keep an eye on performance and uptime. 