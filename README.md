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

From a technical and architectural perspective, the process is as follows:

* The product information from different sources is collected by executing the perform_data_update.py file, which will execute functions to read data from different stores, normalize it, and store it in a MySQL database hosted on Google Cloud.
* Then, in main.py, the data is read and rendered into the front-end using templating and Flask, a web application library. The front-end utilizes HTML, CSS, and JavaScript embedded within the HTML.
* For deploying the web application to the internet, a Google Cloud native service called Google App Engine is used. A new version of the web application based on the latest version in the repository is automatically deployed to the Google App Engine.

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

### Deployment diagram
![gcp deploy](https://github.com/user-attachments/assets/2fd50b65-3436-4224-865c-e562b1ebd567)

### Data flow diagram

### Use case diagram

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
   - **Region**: `europe-north1` (recommended for cost).  
   - **Machine Type**: Shared core, 1 vCPU, 0.614 GB RAM.  
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

