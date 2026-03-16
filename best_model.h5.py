# Part 1: Imports and Data Extraction
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datasets import load_dataset

# Function to scrape and clean text from URLs
def scrape_policy(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove unwanted tags (scripts, styles, headers, footers)
        for element in soup(['script', 'style', 'header', 'footer', 'nav']):
            element.decompose()
        # Clean text from extra spaces
        text = ' '.join(soup.get_text().split())
        return text
    except Exception as e:
        return f"Error scraping {url}: {e}"

# Scrape Egyptian Law and GDPR Reference
egypt_law_text = scrape_policy("https://masaar.net/ar/egypt_laws/%D9%82%D8%A7%D9%86%D9%88%D9%86-%D8%AD%D9%85%D8%A7%D9%8A%D8%A9-%D8%A7%D9%84%D8%A8%D9%8A%D8%A7%D9%86%D8%A7%D8%AA-%D8%A7%D9%84%D8%B4%D8%AE%D8%B5%D9%8A%D8%A9/")
gdpr_text = scrape_policy("https://gdpr-info.eu/")

# Load Training Datasets (OPP-115)
dataset = load_dataset("alzoubi36/opp_115", split='train')
df_train = pd.DataFrame(dataset)

print("Scraping and Data Loading Completed.")
# Convert list-type labels to string or take the first element
# Fix: Ensure 'label' column does not contain lists
df_train['label'] = df_train['label'].apply(lambda x: x[0] if isinstance(x, list) else x)

# Now you can safely use get_dummies
labels = pd.get_dummies(df_train['label']).values
# Fix: Join words if the text is a list of words
df_train['text'] = df_train['text'].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))

# Now convert to list for tokenizer
sentences = df_train['text'].tolist()
# Function to clean any unhashable types (lists) in the dataframe
def clean_unhashable(x):
    if isinstance(x, list):
        return ", ".join(map(str, x)) # Convert list to string separated by comma
    return x

# Apply to all columns or specifically to your features/labels
df_train = df_train.applymap(clean_unhashable)
# Part 2: Neural Network for Text Classification
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

# Hyperparameters for best accuracy
vocab_size = 15000
max_length = 300
embedding_dim = 128

# Prepare sentences and labels
sentences = df_train['text'].astype(str).values
labels = pd.get_dummies(df_train['label']).values # Multi-class classification

X_train, X_test, y_train, y_test = train_test_split(sentences, labels, test_size=0.2)

# Tokenization
tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
tokenizer.fit_on_texts(X_train)
train_seq = pad_sequences(tokenizer.texts_to_sequences(X_train), maxlen=max_length)
test_seq = pad_sequences(tokenizer.texts_to_sequences(X_test), maxlen=max_length)

# Neural Network Architecture
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, return_sequences=True)),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.3), # Avoid overfitting
    tf.keras.layers.Dense(labels.shape[1], activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Early stopping to reach the best accuracy without overfitting
early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=3)

model.fit(train_seq, y_train, epochs=10, validation_data=(test_seq, y_test), callbacks=[early_stop])
# Part 2: Optimized Neural Network for High Accuracy
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# 1. Fix the 'unhashable type' error and handle labels
# Ensure labels are flat strings before dummy encoding
df_train['label'] = df_train['label'].apply(lambda x: x[0] if isinstance(x, list) else x)
labels_df = pd.get_dummies(df_train['label'])
labels = labels_df.values
num_classes = labels.shape[1]

# 2. Refined Hyperparameters
vocab_size = 20000  # Increased to capture more legal vocabulary
max_length = 500    # Privacy policies are long, we need more context
embedding_dim = 256 # Richer vector representation
trunc_type = 'post'
padding_type = 'post'
oov_tok = "<OOV>"

# Prepare sentences
sentences = df_train['text'].astype(str).values
X_train, X_test, y_train, y_test = train_test_split(sentences, labels, test_size=0.15, random_state=42)

# 3. Enhanced Tokenization
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(X_train)

train_seq = pad_sequences(tokenizer.texts_to_sequences(X_train), maxlen=max_length, padding=padding_type, truncating=trunc_type)
test_seq = pad_sequences(tokenizer.texts_to_sequences(X_test), maxlen=max_length, padding=padding_type, truncating=trunc_type)

# 4. Advanced Model Architecture
# Added SpatialDropout and multiple Dense layers for better feature extraction
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    tf.keras.layers.SpatialDropout1D(0.4), # Specialized dropout for NLP
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True)),
    tf.keras.layers.Bidirectional(tf.keras.layers.GRU(64)), # Added GRU layer for deeper learning
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.BatchNormalization(), # Normalizes inputs for faster convergence
    tf.keras.layers.Dense(num_classes, activation='softmax')
])

# 5. Learning Rate Scheduling
# Starting with a slightly higher LR and reducing it helps hit the global minimum
initial_learning_rate = 0.001
lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate, decay_steps=1000, decay_rate=0.9
)

optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)

model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

# 6. Improved Callbacks
# Save the best model only and stop early if val_loss stops improving
checkpoint = tf.keras.callbacks.ModelCheckpoint('best_model.h5', monitor='val_accuracy', save_best_only=True, mode='max')
early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# 7. Training with Class Weights (Optional but recommended if data is imbalanced)
history = model.fit(
    train_seq, y_train,
    epochs=30,
    batch_size=32,
    validation_data=(test_seq, y_test),
    callbacks=[early_stop, checkpoint],
    verbose=1
)
# --- Part 3: Gemini Integration with your API Key ---
import google.generativeai as genai
from google.colab import userdata

# 1. الآمان أولاً: استدعاء المفتاح من "Secrets" في كولاب
# تأكدي من إضافة اسم GEMINI_API_KEY في قائمة المفاتيح يسار كولاب
try:
    API_KEY = userdata.get('GEMINI_API_KEY')
    genai.configure(api_key=API_KEY)
    print("✅ Gemini is now connected and ready!")
except Exception as e:
    print(f"❌ Error: Make sure you added 'GEMINI_API_KEY' to Colab Secrets. Details: {e}")

# 2. تحديد الموديل
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

def get_compliance_report(policy_text, law_context, region="Egypt"):
    """
    This function sends your data to Gemini to perform the legal analysis.
    """
    prompt = f"""
    You are a professional legal auditor specializing in {region} data protection laws.

    Reference Law (The Truth):
    {law_context[:3500]}

    The Privacy Policy to Analyze:
    {policy_text[:2500]}

    Tasks:
    1. Identify specific violations of the {region} law found in the policy.
    2. Explain in simple, friendly Arabic for an Egyptian citizen what this means for their privacy.
    3. Provide a 'Compliance Score' from 1 to 10.
    """

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during analysis: {e}"

# --- 3. Example Execution ---
# الآن يمكنك استدعاء الدالة لتعمل فعلياً
# egypt_report = get_compliance_report(policy_text_variable, egypt_law_text, "Egypt")
# print(egypt_report)
