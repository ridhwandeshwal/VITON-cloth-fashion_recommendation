# ReVeRa: AI-Powered Fashion Recommendation and Virtual Try-On Platform

ReVeRa is an AI-integrated fashion web application that empowers users to receive **personalized clothing recommendations**, **try on outfits virtually**, and **style garments interactively** — all through a seamless digital experience. From visual recommendations to real-time style assistance and neural image transformations, ReVeRa is the future of online fashion.

---

## Overview

ReVeRa bridges deep learning with fashion e-commerce by combining:
- Virtual Try-On using **VITON-HD** and **Graphonomy-based segmentation**,
- A **Knowledge Graph-powered recommendation system** enhanced by **LLaVA** for visual attribute extraction,
- A **fashion chatbot** that offers contextual outfit guidance, and
- An artistic **Neural Style Transfer** module for creative garment transformations.

---

## Features

### 1. Virtual Try-On (VTON)

- Uses **VITON-HD** for high-fidelity garment warping and try-on.
- Enhanced with **Graphonomy segmentation** for parsing body parts.
- **Canny Edge Detection** sharpens segmentation boundaries.
- **OpenPose** extracts body keypoints for pose-aware alignment.
- Output is overlaid on the user’s uploaded image for a realistic try-on effect.

### 2. AI-Powered Fashion Recommendation System

- Based on a **Knowledge Graph** with 11.6k+ fashion items as nodes.
- Attributes like Category, Color, Pattern, Brand, Occasion, etc. are auto-extracted via **LLaVA** (Vision-Language Model).
- Supports:
  - **Cold Start** handling via Style Quiz with drag-and-drop interface.
  - **Search-based Recommendation** using **Named Entity Recognition (NER)** on user queries.
  - **Image-specific Recommendations** by matching visual/stylistic features in the graph.

### 3. Neural Style Transfer (NST)

- Users can apply artistic styles (sketch, watercolor, abstract) or blend two garments.
- Implemented using **VGG-19** to extract content & style features.
- Output can lead to:
  - **Custom-made item ordering**,
  - **style-based garment recommendations**.

### 4. Fashion-Bot: “What the Frock!”

- Intelligent virtual stylist chatbot.
- Offers complete outfit advice based on image + context.
- Factors in:
  - Occasion, Weather, Personal Preferences
  - Suggests accessories, bottoms, footwear, hair, makeup, and layering.

---

## Tech Stack

- **Frontend:** HTML, CSS, JS, React (for recommendation UI)
- **Backend:** FastAPI (REST endpoints for model interaction)
- **VTON Models:** VITON-HD, Graphonomy
- **Vision Models:** OpenPose, SCHP
- **Vision-Language Model:** LLaVA
- **Search NLP:** spaCy (NER)
- **Graph DB:** NetworkX / Neo4j-like graph for recommendations

---

## Dataset & Tools

-  **Given VITON-HD Dataset** for try-on garment pairs.
-  **Pretrained Models Used:**
  - `VITON-HD` (cloth warping)
  - `Graphonomy` (human parsing)
  - `OpenPose` (keypoints)
  - `LLaVA` (vision-language attribute labeling)
-  **Tools:** Canny Edge Detector, Drag-n-drop style quiz UI, FastAPI backend APIs.

---

##  Preprocessing Workflow

graph TD
    A[User Uploads Image] --> B[Run Graphonomy]
    B --> C[Edge Refinement (Canny)]
    C --> D[Pose Keypoints via OpenPose]
    D --> E[Cloth Warping using VITON-HD]
    E --> F[Final Try-On Output]

--------------------------------------------------------------------------------------------------------
**UI Preview**

Style quiz: A drag and drop rank-based quiz to assign weights to user's preferences, leading to more personal recommendations.

Home Page: Personalized recommendations shown immediately post-quiz.

Cloth Detail Page: Try-on interface + style-bot fashion suggestions + similar item recommendations + neural style transfer options + with 2 branches - buying the custom-made piece
                                                - recommendations matching the custom item

Fashion-bot: Conversation UI for "What the Frock?! Style-bot" assistant.

Search Page: Search-based recommendations based on Named Entity Recognition. Also provides attribute options to filter out preferences from search results.

--------------------------------------------------------------------------------------------------------
**Educational Value**

This project was built as a full-stack AI solution, covering:
-Deep learning model integration (VTON, segmentation, NST)
-Knowledge graph construction and querying
-API design using FastAPI
-User-centered frontend development
-Multimodal interaction (vision + text)

--------------------------------------------------------------------------------------------------------
**Contributors**
 
-Ridhwan Deshwal --> ridhwandeshwal
-Vivaan Jain --> viv007-cyber
-Riddhi Sharma --> Riddhi-Sharma27

--------------------------------------------------------------------------------------------------------





