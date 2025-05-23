# MMUSDA Church Payment System

A Django-based payment system for MMUSDA church with M-Pesa integration.

## Features

- Family and Cohort Management
- Member Registration with Phone Number Authentication
- M-Pesa Integration for:
  - Offerings
  - Tithes
  - Contributions
  - Mission Payments (20 bob weekly, 50 bob monthly)
  - Lunch Money
  - Fundraising

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd paymentservices
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your M-Pesa credentials:
```env
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_PASSKEY=your_passkey
MPESA_PAYBILL=your_paybill
MPESA_CALLBACK_URL=your_callback_url
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

- `payments/`: Main app containing payment logic and M-Pesa integration
- `mmusda/`: Project settings and configuration
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript, images)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 