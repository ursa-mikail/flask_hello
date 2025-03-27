# chmod +x run.sh
# ./run.sh

# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
# Run the Flask app (on background)
#nohup python app.py -b > output.log 2>&1 &