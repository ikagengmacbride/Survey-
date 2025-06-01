from flask import Flask, render_template, request, redirect, url_for
import datetime

app = Flask(__name__)

# Dummy database (replace with a real database in a production app)
survey_data = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        full_names = request.form['name']
        email = request.form['email']
        dob_str = request.form['dob'] # Get date of birth as string
        contact_number = request.form['contact']
        food_choices = request.form.getlist('food')
        
        # Ratings
        movies_rating = request.form['i_like_to_watch_movies']
        radio_rating = request.form['i_like_to_listen_to_radio']
        eat_out_rating = request.form['i_like_to_eat_out']
        tv_rating = request.form['i_like_to_watch_tv']

        dob_error = None # Initialize error variable for general DOB issues
        age_error = None # Initialize error variable for age validation

        # Date of Birth and Age Validation
        if dob_str:
            try:
                dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
                
                # Check if DOB is in the future
                if dob > datetime.date.today():
                    dob_error = "Date of Birth cannot be in the future."
                else:
                    # Calculate age
                    today = datetime.date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    
                    # Age range validation (5 to 120 years)
                    if age < 5 or age > 120:
                        age_error = "Age must be between 5 and 120 years."
            except ValueError:
                dob_error = "Invalid Date of Birth format. Please use ISO 8601 (YYYY-MM-DD)."
        else:
            dob_error = "Date of Birth is required." # This might not be hit if browser enforces it.

        # If any error exists, re-render the form with messages
        if dob_error or age_error:
            return render_template('survey.html', 
                                   dob_error=dob_error,
                                   age_error=age_error, # Pass the new age error
                                   # Pass back other submitted values to re-populate the form
                                   name=full_names,
                                   email=email,
                                   dob=dob_str, # Pass dob_str back for value attr
                                   contact=contact_number,
                                   food=food_choices, # Pass as list to re-check boxes
                                   i_like_to_watch_movies=movies_rating,
                                   i_like_to_listen_to_radio=radio_rating,
                                   i_like_to_eat_out=eat_out_rating,
                                   i_like_to_watch_tv=tv_rating
                                )

        # If no error, proceed to save data
        survey_data.append({
            'full_names': full_names,
            'email': email,
            'dob': dob_str,
            'contact_number': contact_number,
            'food_choices': food_choices,
            'ratings': {
                'movies': int(movies_rating),
                'radio': int(radio_rating),
                'eat_out': int(eat_out_rating),
                'tv': int(tv_rating)
            }
        })
        return redirect(url_for('results')) # Redirect to results after successful submission
    
    # This block handles the initial GET request to '/'
    # Initialize variables to None or empty for first load to prevent UndefinedError
    return render_template('survey.html', 
                           name=None, 
                           email=None, 
                           dob=None, 
                           contact=None, 
                           food=[], # Empty list for checkboxes
                           i_like_to_watch_movies=None, 
                           i_like_to_listen_to_radio=None, 
                           i_like_to_eat_out=None, 
                           i_like_to_watch_tv=None
                        )

@app.route('/results')
def results():
    if not survey_data:
        return render_template('results.html', message="No survey data available yet.")

    total_surveys = len(survey_data)

    # Age calculations for results page
    today = datetime.date.today()
    ages = []
    for survey in survey_data:
        dob_str = survey['dob']
        try:
            dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            ages.append(age)
        except ValueError:
            # Handle cases where DOB might be invalidly stored or skipped
            pass
    
    # Ensure ages list is not empty before calculating min/max/average
    average_age = round(sum(ages) / len(ages)) if ages else 0
    oldest = max(ages) if ages else 0
    youngest = min(ages) if ages else 0

    # Food preferences calculations
    pizza_count = sum(1 for s in survey_data if 'Pizza' in s['food_choices'])
    pasta_count = sum(1 for s in survey_data if 'Pasta' in s['food_choices'])
    pap_wors_count = sum(1 for s in survey_data if 'Pap and Wors' in s['food_choices'])

    pizza_percent = round((pizza_count / total_surveys) * 100) if total_surveys > 0 else 0
    pasta_percent = round((pasta_count / total_surveys) * 100) if total_surveys > 0 else 0
    pap_wors_percent = round((pap_wors_count / total_surveys) * 100) if total_surveys > 0 else 0

    # Average ratings calculations
    movies_total = sum(s['ratings']['movies'] for s in survey_data)
    radio_total = sum(s['ratings']['radio'] for s in survey_data)
    eat_out_total = sum(s['ratings']['eat_out'] for s in survey_data)
    tv_total = sum(s['ratings']['tv'] for s in survey_data)

    movies_avg = round(movies_total / total_surveys, 1) if total_surveys > 0 else 0
    radio_avg = round(radio_total / total_surveys, 1) if total_surveys > 0 else 0
    eat_out_avg = round(eat_out_total / total_surveys, 1) if total_surveys > 0 else 0
    tv_avg = round(tv_total / total_surveys, 1) if total_surveys > 0 else 0

    return render_template('results.html',
                           total=total_surveys,
                           average_age=average_age,
                           oldest=oldest,
                           youngest=youngest,
                           pizza_percent=pizza_percent,
                           pasta_percent=pasta_percent,
                           pap_wors_percent=pap_wors_percent,
                           movies_avg=movies_avg,
                           radio_avg=radio_avg,
                           eat_out_avg=eat_out_avg,
                           tv_avg=tv_avg)

if __name__ == '__main__':
    app.run(debug=True)