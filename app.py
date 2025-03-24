import streamlit as st
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import json
from io import BytesIO
import base64

# Instead of this:
# ADMIN_PASSWORD = "admin123"  # Hardcoded password

# Use this:
# Get the admin password from secrets
# If not found, use a default (but this should only be for development)
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")

# Set page configuration
st.set_page_config(
    page_title="Word Cloud Poll",
    page_icon="☁️",
    layout="wide"
)

# Initialize session state for data persistence
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'view_all_clouds' not in st.session_state:
    st.session_state.view_all_clouds = False
if 'config' not in st.session_state:
    st.session_state.config = {
        "current_question": 0,
        "questions_enabled": [True, False, False],
        "poll_completed": False
    }
if 'word_clouds' not in st.session_state:
    st.session_state.word_clouds = [[], [], []]  # Empty lists for each question


# Define the three questions
QUESTIONS = [
    "What one word would you use to describe our team's journey during the last PI?",
    "What's one small habit or practice that helped you stay productive during the last PI?",
    "If you could have a superpower to improve our next PI, what would it be?"
]

# Common English stop words
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'for',
    'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
    'will', 'just', 'don', 'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our',
    'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
    'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they',
    'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
    'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'would', 'should',
    'could', 'ought', 'i\'m', 'you\'re', 'he\'s', 'she\'s', 'it\'s', 'we\'re', 'they\'re',
    'i\'ve', 'you\'ve', 'we\'ve', 'they\'ve', 'i\'d', 'you\'d', 'he\'d', 'she\'d', 'we\'d',
    'they\'d', 'i\'ll', 'you\'ll', 'he\'ll', 'she\'ll', 'we\'ll', 'they\'ll', 'isn\'t',
    'aren\'t', 'wasn\'t', 'weren\'t', 'hasn\'t', 'haven\'t', 'hadn\'t', 'doesn\'t',
    'don\'t', 'didn\'t', 'won\'t', 'wouldn\'t', 'shan\'t', 'shouldn\'t', 'can\'t',
    'cannot', 'couldn\'t', 'mustn\'t', 'let\'s', 'that\'s', 'who\'s', 'what\'s', 'here\'s',
    'there\'s', 'when\'s', 'where\'s', 'why\'s', 'how\'s', 'as', 'of', 'get', 'got', 'gets'
}

def process_text(text):
    """
    Process the input text by tokenizing and removing stop words.
    Returns a list of processed words.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace non-alphanumeric with spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Split into words
    words = text.split()
    
    # Remove stop words and ensure words are alphabetic
    processed_words = [
        word for word in words 
        if word not in STOP_WORDS and word.isalpha() and len(word) > 1
    ]
    
    return processed_words

def generate_word_cloud(words):
    """
    Generate a word cloud from a list of words.
    Font size ranges from 8 to 60 based on frequency.
    """
    # Count word frequencies
    word_counts = Counter(words)
    
    # Create word cloud with specified font size range
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        min_font_size=8,
        max_font_size=60,
        colormap='viridis'
    ).generate_from_frequencies(word_counts)
    
    return wordcloud

def get_image_download_link(fig, filename, text):
    """Generate a link to download the word cloud as an image."""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">Download {text}</a>'
    return href

def admin_section():
    """Admin section for controlling the questions"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Admin Controls")
    
    # Get admin password from secrets
    # In production, this will be set in Streamlit Cloud
    # For local development, it will use the value from .streamlit/secrets.toml
    # If neither is available, it falls back to a default (which you should change)
    ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")
    
    # Password protection
    if not st.session_state.admin_authenticated:
        admin_password = st.sidebar.text_input("Admin Password", type="password")
        
        if st.sidebar.button("Login"):
            if admin_password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.sidebar.success("Admin access granted")
                st.rerun()
            else:
                st.sidebar.error("Incorrect password")
    else:
        st.sidebar.success("Admin access granted")
        
        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.admin_authenticated = False
            st.session_state.view_all_clouds = False
            st.rerun()
        
        # Get current configuration from session state
        config = st.session_state.config
        current_question = config["current_question"]
        questions_enabled = config["questions_enabled"]
        
        # Show current status
        st.sidebar.write(f"Current Question: {current_question + 1} of {len(QUESTIONS)}")
        
        # Controls for each question
        for i, enabled in enumerate(questions_enabled):
            status = "Enabled" if enabled else "Disabled"
            st.sidebar.write(f"Question {i + 1}: {status}")
        
        # Enable/disable questions
        if st.sidebar.button("Enable Next Question"):
            if current_question < len(QUESTIONS) - 1:
                # Disable all questions
                questions_enabled = [False] * len(QUESTIONS)
                # Enable only the next question
                questions_enabled[current_question + 1] = True
                # Update the current question index to the newly enabled one
                config["current_question"] = current_question + 1
                config["questions_enabled"] = questions_enabled
                st.session_state.config = config
                st.sidebar.success(f"Question {current_question + 2} enabled and set as current!")
                st.rerun()
            else:
                st.sidebar.warning("All questions are already enabled.")
        
        # Change current question
        new_question = st.sidebar.selectbox(
            "Set Current Question", 
            range(1, len(QUESTIONS) + 1),
            index=current_question
        )
        
        if st.sidebar.button("Set as Current Question"):
            # Disable all questions
            questions_enabled = [False] * len(QUESTIONS)
            # Enable only the selected question
            questions_enabled[new_question - 1] = True
            config["current_question"] = new_question - 1
            config["questions_enabled"] = questions_enabled
            st.session_state.config = config
            st.sidebar.success(f"Question {new_question} enabled and set as current")
            st.rerun()
            
        # View all word clouds
        st.session_state.view_all_clouds = st.sidebar.checkbox(
            "View All Word Clouds", 
            value=st.session_state.view_all_clouds
        )
        
        # Complete Poll button (show all results to all users)
        if st.sidebar.button("Complete Poll & Show Results"):
            config["poll_completed"] = True
            st.session_state.config = config
            st.sidebar.success("Poll completed! All users will now see the results.")
            st.rerun()
            
        # Reset Poll button
        if config.get("poll_completed", False):
            if st.sidebar.button("Reset Poll"):
                config["poll_completed"] = False
                config["current_question"] = 0
                config["questions_enabled"] = [True, False, False]
                st.session_state.config = config
                st.sidebar.success("Poll has been reset!")
                st.rerun()

# Main application
def main():
    st.title("Word Cloud Poll")
    
    # Get configuration from session state
    config = st.session_state.config
    current_question = config["current_question"]
    questions_enabled = config["questions_enabled"]
    poll_completed = config.get("poll_completed", False)
    
    # Show admin section
    admin_section()
    
    # Check if poll is completed - show results mode
    if poll_completed:
        display_results_mode()
    else:
        # Regular poll mode
        display_poll_mode(current_question, questions_enabled)
    
def display_results_mode():
    """Display all word clouds in results mode"""
    st.header("Poll Results")
    st.success("Thank you for participating in our poll! Here are the results from all questions:")
    
    # Sidebar for refresh in results mode
    st.sidebar.title("Refresh")
    refresh_clicked = st.sidebar.button("Refresh Results", help="Manually refresh to see latest results")
    if refresh_clicked:
        st.sidebar.success("✓ Results refreshed!")
        st.rerun()
    
    # Display all word clouds
    for i in range(len(QUESTIONS)):
        words = st.session_state.word_clouds[i]
        if words:
            st.markdown("---")
            st.subheader(f"Question {i + 1}: {QUESTIONS[i]}")
            
            # Generate word cloud
            wordcloud = generate_word_cloud(words)
            
            # Display the word cloud using matplotlib
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
            
            # Add download option
            st.markdown(get_image_download_link(fig, f"word_cloud_q{i + 1}.png", "Download Word Cloud Image"), unsafe_allow_html=True)
            
            # Display statistics
            word_counts = Counter(words)
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Total unique words: {len(word_counts)}")
                st.write(f"Total words added: {len(words)}")
            
            with col2:
                st.write("Top 5 Frequent Words:")
                top_words = word_counts.most_common(5)
                for word, count in top_words:
                    st.write(f"• {word}: {count}")
        else:
            st.write(f"Question {i + 1}: No responses were collected")

def display_poll_mode(current_question, questions_enabled):
    """Display the poll interface for collecting responses"""
    # Display current question
    st.header(f"Question {current_question + 1}")
    st.write(QUESTIONS[current_question])
    
    # Check if the current question is enabled
    if not questions_enabled[current_question]:
        st.warning("This question is currently disabled. Please wait for the admin to enable it.")
    
    # Sidebar for refresh controls
    st.sidebar.title("Refresh")
    
    # Manual refresh button
    refresh_clicked = st.sidebar.button("Refresh Word Cloud", help="Manually refresh to see updates from other users")
    
    if refresh_clicked:
        st.sidebar.success("✓ Word cloud refreshed!")
        st.rerun()
    
    # Text input field
    user_input = st.text_area("Enter your text:", height=150)
    
    # Button to add words to the cloud
    add_button = st.button("Add to Word Cloud")
    
    # Only allow adding words if the current question is enabled or if admin is logged in
    if add_button:
        if not questions_enabled[current_question] and not st.session_state.admin_authenticated:
            st.error("This question is currently disabled. You cannot add words at this time.")
        elif not user_input:
            st.warning("Please enter some text first.")
        else:
            # Process the input text
            processed_words = process_text(user_input)
            
            # Get current words from session state
            current_words = st.session_state.word_clouds[current_question]
            
            # Add new words
            current_words.extend(processed_words)
            
            # Save updated words back to session state
            st.session_state.word_clouds[current_question] = current_words
            st.success(f"Added {len(processed_words)} words to the word cloud!")
            # Refresh to display updated cloud
            st.rerun()
    
    # Get current words
    words = st.session_state.word_clouds[current_question]
    
    # Display the word cloud if there are words
    if words:
        st.subheader(f"Word Cloud for Question {current_question + 1}")
        
        # Generate word cloud
        wordcloud = generate_word_cloud(words)
        
        # Display the word cloud using matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        
        # Add download option
        st.markdown(get_image_download_link(fig, f"word_cloud_q{current_question + 1}.png", "Download Word Cloud Image"), unsafe_allow_html=True)
        
        # Display statistics in sidebar
        st.sidebar.subheader("Word Statistics")
        word_counts = Counter(words)
        st.sidebar.write(f"Total unique words: {len(word_counts)}")
        st.sidebar.write(f"Total words added: {len(words)}")
        
        # Display top 5 most frequent words
        st.sidebar.subheader("Top 5 Frequent Words")
        top_words = word_counts.most_common(5)
        for word, count in top_words:
            st.sidebar.write(f"{word}: {count}")
    else:
        st.info("The word cloud will appear here after you add some words.")
    
    # Show other word clouds if admin requested
    if st.session_state.admin_authenticated and st.session_state.view_all_clouds:
        st.markdown("---")
        st.header("All Word Clouds")
        
        for i in range(len(QUESTIONS)):
            if i != current_question:  # Skip current question as it's already shown
                words = st.session_state.word_clouds[i]
                if words:
                    st.subheader(f"Question {i + 1}: {QUESTIONS[i]}")
                    wordcloud = generate_word_cloud(words)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                else:
                    st.write(f"Question {i + 1}: No responses yet")
    
    # Add app information
    st.sidebar.title("About This App")
    st.sidebar.info("""
    This Word Cloud Poll application allows multiple users to contribute text to a shared word cloud.

    **How it works:**
    1. Enter your text in the input box
    2. Click "Add to Word Cloud" 
    3. Words appear in the cloud with size based on frequency

    **Collaboration:**
    - Click the "Refresh Word Cloud" button to see updates from other users
    """)

# Run the main application
if __name__ == "__main__":
    main()