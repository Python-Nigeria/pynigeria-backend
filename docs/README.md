# PyNigeria Backend
### This is the backend of the official website of Python Nigeria



### Current Features
- Job listing
- Job application
---

### Prerequisites

Before starting, ensure you have the following installed:
- Python (>= 3.10)
- [uv](https://docs.astral.sh/uv/) (package manager)
- PostgreSQL/MySQL (or any database of choice)

---

### Installation

Follow these steps to set up the project locally:

1. **Install uv:**
   ```bash
   pip install uv
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/Python-Nigeria/pynigeria-backend.git
   cd pynigeria-backend
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```
   This will automatically create a virtual environment and install all dependencies.

4. **Create a `.env` file and set environment variables:**
   ```plaintext
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=12.34.56,http://127.0.0.1
   CSRF_TRUSTED_ORIGINS=xxxxxxxxx

   DATABASE_URL=your-database-url

   CURRENT_ORIGIN=xxxxxxxxx
   SENDER_EMAIL=xxxxxxxxx
   EMAIL_BACKEND=xxxxxxxxx
   EMAIL_HOST=xxxxxxxxx
   EMAIL_PORT=xxxxxxxxx
   EMAIL_USE_TLS=xxxxxxxxx
   EMAIL_HOST_USER=xxxxxxxxx
   EMAIL_HOST_PASSWORD=xxxxxxxxx
   ```

5. **Apply migrations:**
   ```bash
   uv run python manage.py migrate
   ```

6. **Run the server:**
   ```bash
   uv run python manage.py runserver
   ```

The server will be available at `http://127.0.0.1:8000/`.

---

### Testing

Run tests using the following command:
```bash
uv run python manage.py test
```

---

### Contributing

Contributions are welcome! Follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

---

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Contact

    •  Author Name: [Your Name]
    •  Email: [your.email@example.com]
    •  GitHub: [https://github.com/username](https://github.com/username)
