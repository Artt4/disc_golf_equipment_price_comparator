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
The Data Flow Diagram below explains how data moves through the Disc Golf Equipment Price Comparator system. It shows interactions between the user, internal services (like the front-end, authentication, scraper, and recommender), external data sources, and the Cloud SQL database. User actions trigger data retrieval, authentication, and recommendation processes, while background services ensure that product data is kept up-to-date.

Key processes such as authentication are marked as optional (`opt`), the scraper runs on a scheduled loop (`loop`), and background updates happen in parallel (`par`). These markers help visualize conditional, repetitive, and parallel operations within the system.

![data_flow](https://github.com/user-attachments/assets/a683896d-f04d-41c3-8c2f-5dcf7eeb684c)


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

