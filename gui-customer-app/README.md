# GUI Customer Application

This project is a graphical user interface (GUI) application that allows users to input customer names and ages, and displays the list of customers as requested.

## Project Structure

```
gui-customer-app
├── src
│   ├── main.py          # Entry point of the application
│   ├── gui
│   │   └── app.py      # Contains the CustomerApp class for GUI
│   ├── models
│   │   └── customer.py  # Defines the Customer class
│   └── utils
│       └── __init__.py  # Utility functions and constants
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Requirements

To run this application, you need to install the required dependencies. You can do this by running:

```
pip install -r requirements.txt
```

## Running the Application

To start the application, run the following command:

```
python src/main.py
```

This will initialize the GUI and start the main event loop, allowing you to interact with the application.

## Features

- Input customer names and ages
- Display a list of customers
- User-friendly interface for easy interaction

## Contributing

Feel free to fork the repository and submit pull requests for any improvements or features you would like to add.