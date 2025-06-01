# Age & Era Calculator 📅

A Streamlit web application that calculates a person's culturally significant life periods—childhood, teenage years, and young adulthood—based on their date of birth or age. It also determines their star sign, generation, and provides a personalized cultural snapshot for those eras using AI (OpenAI GPT-3.5-turbo).

## Features ✨

*   **Flexible Input**: Calculate based on either Date of Birth (DOB) or current age.
*   **Era Calculation**: Identifies key impressionable periods:
    *   Childhood: Ages 5-12
    *   Teenage Years: Ages 13-19
    *   Young Adult Years: Ages 20-29
*   **Astrological Sign**: Displays the user's zodiac sign.
*   **Generational Cohort**: Identifies the user's generation (e.g., Millennial, Gen Z).
*   **Personalized Cultural Snapshot**: Leverages OpenAI's GPT model to generate a summary of key cultural, technological, and political influences relevant to the user's formative years in their specified country.
*   **Shareable ID**: Generates a unique ID representing the input, allowing users to (conceptually) share their results (Note: full sharing functionality would require a backend database).
*   **User-Friendly Interface**: Built with Streamlit for a clean and interactive experience.

## How to Run Locally 🚀

### Prerequisites

*   Python 3.8 or newer
*   pip (Python package installer)

### Installation

1.  **Clone the repository (or download the source code):**
    ```bash
    git clone https://github.com/your-username/age-and-era-calculator.git # Replace with your actual repo URL if different
    cd age-and-era-calculator
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

To use the AI-powered cultural snapshot feature, you need an OpenAI API key.

1.  Create a file named `.env` in the root directory of the project.
2.  Add your OpenAI API key to this file:
    ```
    OPENAI_API_KEY='your_openai_api_key_here'
    ```
    Replace `'your_openai_api_key_here'` with your actual key. If you don't have one, you can obtain it from [OpenAI](https://platform.openai.com/account/api-keys).

    *Note: If the API key is not provided or invalid, the cultural snapshot feature will display placeholder text.*

### Running the App

Once the dependencies are installed and the `.env` file is set up (if using the AI feature), run the Streamlit application:

```bash
streamlit run app.py
```

This will typically open the application in your default web browser (e.g., at `http://localhost:8501`).

## Technologies Used 🛠️

*   **Python**: Core programming language.
*   **Streamlit**: For the web application interface.
*   **OpenAI API (GPT-3.5-turbo)**: For generating personalized cultural summaries.
*   **python-dotenv**: For managing environment variables (API key).

## Future Enhancements (Ideas) 💡

*   More detailed cultural context inputs (e.g., specific interests, subcultures).
*   Integration with external APIs for music, movies, or news from specific eras.
*   User accounts and a database to save and truly share results via links.
*   Enhanced UI/UX with more customization options.
*   More sophisticated error handling for API calls.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/your-username/age-and-era-calculator/issues) (if you plan to host this on GitHub).

---

This README provides a good starting point. You might want to customize the repository URL and contribution links if you host this publicly.
