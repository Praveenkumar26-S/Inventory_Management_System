## **Flask Inventory Management Web Application**

This is a simple Inventory Management System built using **Flask** (Python). The app allows you to manage products, locations (warehouses), and product movements, with a clean UI and a balance report.

 ## **Features**
 
**User Authentication**: Login and logout for secure access.

**Product Management**: Add, edit, and delete products with quantity tracking.

**Location Management**: Add, edit, and delete warehouse locations.

**Product Movement**: Record movements (Unknown to Hub, Hub to Hub, Hub to Customer) with business logic enforced.

**Inventory Report**: View real-time product balances at each location in a table.

**Modern UI**: Responsive, interactive design with enhanced CSS.

**SQLite Database**: Simple, file-based storage for easy setup.

##  Screenshots
1. Login page
![Login](https://github.com/user-attachments/assets/9ea2fa9e-b559-4753-96ae-7e7e4b518727)

2. User Name and Password
![username](https://github.com/user-attachments/assets/d906ecbc-7389-4bb1-a405-2dd684198d89)

3. Home Page
![home](https://github.com/user-attachments/assets/e3e13567-ac46-4888-81dd-d5b5879b0c40)

4. Products
![Products](https://github.com/user-attachments/assets/4f7c8ca1-57ac-49e2-8a47-e3cfcbc98057)

5. Locations
![Locations](https://github.com/user-attachments/assets/3d195eae-facc-4b80-aea2-d5a74961f7b9)

6. Product Movements
![Product Movement](https://github.com/user-attachments/assets/63178c4e-20c2-4236-a016-cf9f17fa3856)

7. Report Page
![Report](https://github.com/user-attachments/assets/77789612-6efc-473f-930a-df871fc9b2ba)

8.Logout Page
![Logout](https://github.com/user-attachments/assets/07e27e33-30ef-4a31-b5d1-6c7efbde75ff)


##  Getting Started

1. **Clone the Repository**

git clone https://github.com/Praveenkumar26-S/Inventory_Management_System.git

cd Inventory_Management_System

2. **Install Dependencies**

pip install flask flask-sqlalchemy werkzeug

3. **Run the Application**

python app.py


The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

4. **Default Login**

**Username:** `admin`

**Password:** `admin123`

## **Project Structure**

![Project Structure](https://github.com/user-attachments/assets/c6a1643b-236b-47e4-84ba-98547df2474e)


## Database Tables

**Product** (`product_id`, `name`, `quantity`)

**Location** (`location_id`, `name`)

**ProductMovement** (`movement_id`, `timestamp`, `from_location`, `to_location`, `product_id`, `qty`, `movement_type`)

**User** (`id`, `username`, `password_hash`)

## How It Works

**Add products** with a starting quantity.

**Add locations** (warehouses/hubs).

**Record product movements**:

  **Unknown to Hub:** Move from main stock to a hub (decreases main product quantity).
  
  **Hub to Hub:** Move between hubs (only from hubs that have received stock).
    
  **Hub to Customer:** Move out from a hub (does not affect main product quantity).
    
**View reports** to see product balances in each location.

## Demo Video

https://www.linkedin.com/posts/praveenkumar-s-7a0635269_flask-python-webdevelopment-activity-7325490423009792000-w7On?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEHEcSgBiZD0x3wfZ_4qWsh5_p-BFX5gRbk

##  Security

All main routes require login.

Passwords are hashed using Werkzeug.

##  UI/UX

Responsive layout with modern cards and tables.

Animated buttons and hover effects.

Toast-style flash messages for feedback.

## Contact

**G-Mail:** kumarpraveen97917@gmail.com
