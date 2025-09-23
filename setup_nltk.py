"""
NLTK Setup Script
Add this to your repo and import it in app.py to ensure NLTK data is downloaded
"""

import os
import sys

def setup_nltk():
    """Download required NLTK data for TextBlob and sentiment analysis"""
    try:
        import nltk
        
        # Set NLTK data path to a writable location
        nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)
        
        # Download required datasets
        datasets = [
            'punkt',
            'stopwords', 
            'averaged_perceptron_tagger',
            'brown',
            'movie_reviews'
        ]
        
        for dataset in datasets:
            try:
                nltk.data.find(f'tokenizers/{dataset}')
                print(f"✅ NLTK {dataset} already available")
            except LookupError:
                try:
                    nltk.data.find(f'corpora/{dataset}')
                    print(f"✅ NLTK {dataset} already available")
                except LookupError:
                    try:
                        nltk.data.find(f'taggers/{dataset}')
                        print(f"✅ NLTK {dataset} already available")
                    except LookupError:
                        try:
                            print(f"Downloading NLTK {dataset}...")
                            nltk.download(dataset, quiet=True)
                            print(f"✅ NLTK {dataset} downloaded")
                        except Exception as e:
                            print(f"❌ Failed to download NLTK {dataset}: {e}")
        
        # Test TextBlob functionality
        try:
            from textblob import TextBlob
            test_blob = TextBlob("This is a test sentence for sentiment analysis.")
            sentiment = test_blob.sentiment
            print(f"✅ TextBlob working: polarity={sentiment.polarity:.2f}")
            return True
        except Exception as e:
            print(f"❌ TextBlob test failed: {e}")
            return False
            
    except ImportError:
        print("❌ NLTK not installed")
        return False
    except Exception as e:
        print(f"❌ NLTK setup failed: {e}")
        return False

if __name__ == "__main__":
    print("=== NLTK Setup ===")
    success = setup_nltk()
    if success:
        print("🎉 NLTK setup complete!")
    else:
        print("❌ NLTK setup failed")
