# Disc Golf Equipment Price Comparator

The purpose of the project is to provide a central location for displaying the prices of different disc golf equipment based on data from manufacturers and resellers.

## Introduction

Disc golf, also called frisbee golf, is a rapidly growing sport in the United States, Finland, and Estonia. Here is some insight into the sport:

* https://en.wikipedia.org/wiki/Disc_golf
* https://www.dgpt.com/
* https://www.youtube.com/@JomezPro

Given the growth in the sport, there are currently multiple disc golf equipment manufacturers, such as Discmania, Innova, Dynamic Discs, Latitude 64, and many others, as well as an even wider variety of disc golf equipment resellers. The numerous options can often make it difficult to find the best market deals. Therefore, the idea behind my course project is to compile shop data from both resellers and manufacturers, and aggregate the data into a central location. As mentioned, this aims to help identify the most competitively priced products in the market and even discover unique editions of equipment that are sold exclusively in certain stores. Some of the manufacturer and reseller sites included are listed below, primarily focusing on a scope local to the Nordics and Baltics:

* par3.lv
* discsporteurope.com
* powergrip.fi
* diskiundiskicesis.lv
* latitude64.com
* kiekkokingi.fi

This will enables site visitors to easily search, filter, and compare products between the resellers to make the best choice.

## Technical summary

- **Main Application** (`main.py`): This service contains the main back-end and front-end implementation. On the back-end, it is responsible for pulling data from the databases, parsing the data, handling user authentication, and managing user sessions. After the data is prepared, the system uses it to feed into HTML templates, which are populated and displayed in browsers with applied styling. The HTML and CSS implementation is complemented by scripts written in JavaScript, which implement features to enhance user experience. For example, when applying a search function, the product page resets to the first page. Similarly, these scripts also handle other minor functionalities that improve the overall feel.
- **Recommender Service** (`recommender.py`): Separately from the main application, we have set up the recommender service. This service operates standalone to generate product recommendations for users in their profiles based on patterns of what other users have chosen to add to their wishlists. Essentially, when accessing the main application to check a wishlist, the application performs a GET request from the recommender service to look up the current user's wishlist items and other users' wishlist items, providing the best-fitting recommendations.
- **Scraper Service** (`run_scraper.py`): To gather all product data, we scrape it from disc golf equipment reseller and manufacturer sites. This service is run manually, without a predefined period, to scrape all mapped websites. The period for scraping is undefined and is performed manually as needed to avoid unnecessarily loading the resellers' and manufacturers' websites. The scraped data is cleaned and parsed into the necessary format before being written to the main database, which is used by both the main application and the recommender service.

## System architecture

![gcp drawio](https://github.com/user-attachments/assets/e535325f-faa5-417e-afd4-fa306b0e490e)

### Services overview

1. User (Client)
    - Users interact with the system via a web browser over HTTPS.
    - They can sign in using third-party authentication providers (OAuth).

2. Front-end Service (App Engine)
    - Provides the user interface.
    - Handles user sign-in via OAuth authentication.
    - Fetches product data and personalized recommendations.
    - Communicates with the MySQL database (Cloud SQL) to retrieve and store user information.

3. Authentication (OAuth)
    - OAuth-based authentication is used for user sign-in (Google).
    - After successful authentication, user data is created/stored in Cloud SQL if not already present.

4. Scraper Service (App Engine)
    - Scrapes external data sources (websites) for disc golf equipment pricing.
    - Processes and inserts the collected product information into the Cloud SQL database.
    - Ensures that the product data is up-to-date for user queries and recommendations.

5. Recommender Service (App Engine)
    - Processes user preferences and product data to generate tailored equipment recommendations.
    - Reads product and user data from Cloud SQL.
    - Sends the recommendation results back to the Front-end Service for display to users.

6. Data Sources (External): These are external e-commerce or manufacturer websites from which the Scraper Service extracts pricing and product details.

7. MySQL Database (Cloud SQL)
    - Centralized relational database that stores user profiles and preferences, and product information (scraped from external sources).
    - Shared by all internal services for consistent and synchronized data access.

### Service interactions

- User → Front-end Service: Users access the web app and sign in using OAuth authentication.
- Front-end Service → Authentication Service: The app redirects the user to authenticate via OAuth. If successful, it either fetches or creates the user's profile in Cloud SQL.
- Front-end Service ↔ Cloud SQL: Retrieves user data and product listings to display.
- Scraper Service → External Data Sources: Periodically scrapes disc golf product information and pricing from third-party websites.
- Scraper Service → Cloud SQL: Inserts or updates the latest product information into the database.
- Front-end Service → Recommender Service: Requests recommendations based on user preferences.
- Recommender Service ↔ Cloud SQL: Reads product and user data, computes recommendations, and returns results to the Front-end Service.

### Key properties

- Scalability: App Engine services automatically scale based on traffic and workload.
- Security: All user authentication is handled via secure OAuth providers, and data flows over HTTPS.
- Maintainability: Microservices architecture allows independent updates to scraping logic, recommendation algorithms, and UI without affecting the entire system.

## UML diagrams

### Component diagram
The system includes a web application with a front-end UI and backend API, a recommender service, and a scraper service. The scraper service is composed of multiple store-specific scrapers that gather product data from various sources and store it in a shared MySQL database. The recommender service analyzes user product history and product data to generate personalized recommendations. The web application handles user authentication via Google OAuth and retrieves product and recommendation data from the backend and MySQL.
<p align="center">
  <img
    src="https://github.com/user-attachments/assets/db984ae2-83ab-4539-90a6-1dbf8e7d2ab4"
    alt="Component diagram"
    width="100%"
  />
</p>

### Deployment diagram
Users access the app via a web browser, connecting to front-end, scraper, and recommender microservices running on App Engine. Authentication is handled through Google OAuth with Cloud IAM. All services interact with a MySQL database on Cloud SQL, which stores product and user data in separate schemas. The architecture ensures modularity, scalability, and secure user management.
![gcp deploy](https://github.com/user-attachments/assets/2fd50b65-3436-4224-865c-e562b1ebd567)

### Data flow diagram
The Data Flow Diagram below explains how data moves through the Disc Golf Equipment Price Comparator system. It shows interactions between the user, internal services (like the front-end, authentication, scraper, and recommender), external data sources, and the Cloud SQL database. User actions trigger data retrieval, authentication, and recommendation processes, while background services ensure that product data is kept up-to-date.

Key processes such as authentication are marked as optional (`opt`), the scraper runs on a scheduled loop (`loop`), and background updates happen in parallel (`par`). These markers help visualize conditional, repetitive, and parallel operations within the system.

![data_flow](https://github.com/user-attachments/assets/a683896d-f04d-41c3-8c2f-5dcf7eeb684c)


### Use case diagram
The Use Case diagram models the interactions between a user and a disc golf price comparison system. The user can view products (with options to filter/sort and search), log in using Google, manage a wishlist (add/remove items), and view their profile. Several actions such as wishlist management and profile viewing require prior login.
<p align="center">
  <img
    src="https://github.com/user-attachments/assets/eea92929-4ec9-4fd4-ab55-30b35b1a252b"
    alt="Usecase"
    width="50%"
  />
</p>

## API documentation

| Endpoint               | Method | Parameters (Query/Body)                                                                 | Response                                                                 | Auth Required |
|------------------------|--------|----------------------------------------------------------------------------------------|--------------------------------------------------------------------------|---------------|
| `/login`               | GET    | None                                                                                   | Redirects to Google OAuth                                                | No            |
| `/logout`              | GET    | None                                                                                   | Redirects to `/products`                                                 | Yes           |
| `/auth/callback`       | GET    | OAuth callback params                                                                  | **Success:** Redirects to `/products`<br>**Error:** Error message       | No            |
| `/`                    | GET    | None                                                                                   | Renders `home.html`                                                      | No            |
| `/products`            | GET    | **Query:**<br>`search`, `price_min/max`, `speed_min/max`, `glide_min/max`, `turn_min/max`, `fade_min/max`, `store[]`, `sort`, `page` | Renders `product_grid.html` with filtered products | No            |
| `/profile`             | GET    | None                                                                 | Renders `profile.html` with user data and wishlist                       | Yes           |
| `/add-to-wishlist`     | POST   | **Body (JSON):**<br>`{"currency": str, "fade": int, "glide": int, "image_url": str, "link_to_disc": str, "price": str, "speed": int, "store": str, "title": str, "turn": int, "unique_id": str, "wishlist_count": int}`                                             | `{"success": bool, "message": "Added to wishlist", "unique_id": str}`                    | Yes           |
| `/remove-from-wishlist`| POST   | **Body (JSON):**<br>`{"currency": str, "fade": int, "glide": int, "image_url": str, "link_to_disc": str, "price": str, "speed": int, "store": str, "title": str, "turn": int, "unique_id": str, "wishlist_count": int}`                                              | `{"success": bool, "message": "Removed from wishlist", "unique_id": str}`                    | Yes           |
| `/get-wishlist`        | GET    | None                                                                                   | `{"success": bool, "products": [...]}` or `{"success": false, "message": str}` | Yes       |
| `/recommend`   | GET    | **Query:**<br>`user_id` (required) | **Success:** `{"currency": str, "fade": int, "glide": int, "image_url": str, "link_to_disc": str, "price": str, "speed": int, "store": str, "title": str, "turn": int, "unique_id": str, "wishlist_count": int}`<br>**Error:** `{"title": "No recommendation available", "unique_id": None}` | Yes |

**Setup Guide**  
---

### **Prerequisites**  
1. **Google Cloud Account**: Ensure you have a Google Cloud account with billing enabled.  
2. **Repository Access**: Clone or fork the application repository to your local machine.  
3. **Basic Tools**: Familiarity with Google Cloud Console (GCP) and the `gcloud` CLI.  

---

### **1. Project Setup**  
#### **1.1 Create a New Project**  
1. Navigate to [Google Cloud Console](https://console.cloud.google.com).  
2. Click the project dropdown (top-left) → **New Project**.  
   - Name: `testing-deployment` (or your preferred name).  
3. **Enable Billing**:  
   - Search for "Billing" in the top bar → Link your account.  

#### **1.2 Enable Required APIs**  
1. Open **Cloud Shell** (top-right toolbar).  
2. Set your project ID:  
   ```bash
   gcloud projects list  # Copy the PROJECT_ID
   gcloud config set project PROJECT_ID
   ```  
3. Enable APIs:  
   ```bash
   gcloud services enable \
	artifactregistry.googleapis.com \
	cloudbuild.googleapis.com \
	oslogin.googleapis.com \
	pubsub.googleapis.com \
	run.googleapis.com \
	cloudscheduler.googleapis.com \
	sqladmin.googleapis.com \
	compute.googleapis.com \
	containerregistry.googleapis.com \
	iamcredentials.googleapis.com \
	iam.googleapis.com \
	secretmanager.googleapis.com \
	appengine.googleapis.com \
	artifactregistry.googleapis.com
   ```  

---

### **2. Database Configuration**  
#### **2.1 Create a Cloud SQL Instance**  
1. Search for **"SQL"** in GCP → Create a **MySQL 8.0** instance.  
   - **Instance ID**: `disc-golf-db` (or custom).  
   - **Password**: *Choose a strong password (do not reuse the example!)*.  
   - **Region**: `europe-north1` (or another preferred region).  
   - **Machine Type**: Shared core, 1 vCPU, 0.614 GB RAM (recommended for cost).  
   - **Storage**: 10 GB HDD.  

2. **Create Database**:  
   - Under the **Databases** tab → Name: `main_schema`.  

3. **Create User**:  
   - Under the **Users** tab → Add account:  
     - Username: `app-user`  
     - Password: *Choose a secure password (not the example!)*.  

#### **2.2 Initialize Database Schema**  
1. Navigate to **Cloud SQL Studio** → Select `main_schema`.  
2. Log in with `app-user` credentials.  
3. In the **Editor** tab, run the provided SQL script from the repository. Ensure `USE main_schema;` is the first line.  

---

### **3. OAuth Client Configuration**  
1. Search for **"Google Auth Platform"** → **Create Credentials** → **OAuth Client ID**.  
   - **Application Type**: Web Application.  
   - **Name**: `testing-deployment` (or custom).  
   - **Authorized Redirect URIs**: Temporarily leave blank (configure later).  
2. Download the JSON credentials file. Note the `client_id` and `client_secret`.  

---

### **4. Secret Manager Setup**  
Create the following secrets in **Secret Manager**:  
- `google_secret`: Value = `client_secret` from OAuth JSON.  
- `google_id`: Value = `client_id` from OAuth JSON.  
- `connection_socket`:  
  ```bash
  # Retrieve using:
  gcloud sql instances list --format="table(connectionName)"
  # Format: /cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
  ```  
- `connection_user`: Database username (e.g., `app-user`).  
- `connection_password`: Database user password.  
- `connection_database`: `main_schema`.  
- `SECRET_KEY`: Generate via Cloud Shell:  
  ```bash
  openssl rand -base64 32  # Copy the output.
  ```  

---

### **5. Build and Deploy Services**  
#### **5.1 Artifact Repository**  
```bash
gcloud artifacts repositories create cloud-run-source-deploy \
  --repository-format=docker \
  --location=europe-north1 \
  --description="Images for Disc-Golf app"
```  

#### **5.2 Assign Service Account Roles**  
1. Navigate to **IAM & Admin** → **Service Accounts**.  
2. Edit the **Default Compute Service Account** → Add roles:  
-   Artifact Registry Writer
-   Cloud Functions Invoker
-   Cloud Run Admin
-   Cloud Run Invoker
-   Cloud SQL Client
-   Secret Manager Secret Accessor
-   Service Account User
-   Storage Object Admin 

#### **5.3 Submit Build**  
```bash
cd /path/to/cloned-repo
gcloud builds submit --project=PROJECT_ID
```  

---

### **6. Deploy Services**  
#### **6.1 Scraper Job**  
1. In **Cloud Run** → **Jobs** → **Create Job**:  
   - **Container Image**: Select `scraper_job` from Artifact Registry.  
   - **Region**: `europe-north1`.  
   - **Resources**: 2 vCPU, 2 GB RAM.  
   - **Secrets**: Mount `connection_database`, `connection_password`, `connection_socket`, `connection_user`.  
   - **SQL Connection**: Link your Cloud SQL instance.  

#### **6.2 Recommender Service**  
1. In **Cloud Run** → **Create Service**:  
   - **Container Image**: Select `recommender-service`.  
   - **Allow Unauthenticated Invocations**: Yes.  
   - **Secrets**: Same as scraper.  
   - **SQL Connection**: Link the instance.  

#### **6.3 Frontend Service**  
1. In **Cloud Run** → **Create Service**:  
   - **Container Image**: Select `frontend-service`.  
   - **Add Secrets**: Include all secrets from "Secret Manager Setup" + new secret`recommender_url` (URL of the recommender service).  
   - **Authorized Redirect URI**:  
     - After deployment, note your service URL (e.g., `https://frontend-service-XXXX.run.app`).  
     - Add `http://frontend-service-XXXX.run.app/auth/callback` (HTTP, not HTTPS) to OAuth Client settings.  

