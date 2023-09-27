from flask import Flask, render_template, request, jsonify, g
import sqlite3

app = Flask(__name__)

DATABASE = 'data_collection.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Rest of your database initialization code remains the same...

# Refactored Function with Flask Endpoint
@app.route('/waste_disposal_emissions', methods=['POST'])
def waste_disposal_emissions():
    data = request.json
    age_group = data.get('age_group')
    generated_waste = data.get('generated_waste').lower()

    age_groups = {
        "Below 18 to 30": 30,
        "31 to 50": 36,
        "51 and above": 24
    }

    # DEBUG: Print the received age group for verification
    print("Received age group:", age_group)

    if generated_waste == 'yes':
        waste_weight = age_groups.get(age_group, 0)
    else:
        waste_weight = 0

    output_emissions = waste_weight * 0.700
    #insert_data('waste_disposal_emissions', waste_weight, output_emissions)
    
    return jsonify({"emissions": output_emissions})

# You need to refactor other functions in a similar way...

@app.route('/calculate_travel_emissions', methods=['POST'])
def calculate_travel_emissions():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()

    emission_factors = {
        'air': 0.440,
        'train': 0.072,
        'car': 0.240
    }

    total_emissions = 0
    travel_emissions = {}

    for travel_type, factor in emission_factors.items():
        user_response = data.get(f"{travel_type}_travel").lower()

        if user_response == 'yes':
            distance = float(data.get(f"{travel_type}_distance"))
            emissions = distance * factor
            travel_emissions[travel_type] = emissions
            total_emissions += emissions
            cursor.execute('INSERT INTO collected_data (category, input_data, output_emissions) VALUES (?, ?, ?)',
                           (travel_type + '_travel_emissions', distance, emissions))
            conn.commit()
        elif user_response == 'no':
            cursor.execute('INSERT INTO collected_data (category, input_data, output_emissions) VALUES (?, ?, ?)',
                           (travel_type + '_travel_emissions', 0, 0))
            conn.commit()

    travel_emissions['total'] = total_emissions
    return jsonify(travel_emissions)


@app.route('/calculate_energy_emissions', methods=['POST'])
def calculate_energy_emissions():
    data = request.form

    usage = data.get('energy_usage').lower()
    energy_emissions_data = {}

    if usage == 'yes':
        electricity_bill = float(data.get('electricity_bill'))
        electricity_emissions = electricity_bill * 0.685294118
        energy_emissions_data['electricity'] = electricity_emissions

        gas_meter_type = data.get('gas_meter_type').lower()

        if gas_meter_type in ['imperial', 'metric']:
            gas_bill = float(data.get('gas_bill'))
            gas_emissions_factor = 6.4434483 if gas_meter_type == 'imperial' else 6.4484259
            gas_emissions = gas_bill * gas_emissions_factor
            energy_emissions_data['gas'] = gas_emissions
        else:
            return "Invalid meter type selected.", 400

    elif usage == 'no':
        energy_emissions_data['message'] = "No emissions calculated as no energy was used."
    else:
        return "Invalid selection. Please enter 'yes' or 'no'.", 400

    return jsonify(energy_emissions_data)


@app.route('/calculate_diet_emissions', methods=['POST'])
def calculate_diet_emissions():
    data = request.form

    # Retrieve data from the form
    age_category = data.get('age_category')
    gender = data.get('gender').lower()
    diet_type = data.get('diet_type').lower()

    # Caloric values and conversion factors
    caloric_values = {
        '18 and below': {'male': 72000, 'female': 58500},
        '19-30': {'male': 80400, 'female': 62400},
        '31-50': {'male': 77000, 'female': 60000},
        '51 and above': {'male': 70000, 'female': 55000}
    }

    conversion_factors = {
        'vegan': 0.00069,
        'vegetarian': 0.00116,
        'omnivorous': 0.00223,
        'pescetarian': 0.00166,
        'paleo': 0.00262,
        'keto': 0.00291
    }

    # Calculate emissions
    if all(key in caloric_values for key in [age_category]) and gender in ['male', 'female'] and diet_type in conversion_factors:
        user_input = caloric_values[age_category][gender]
        conversion_factor = conversion_factors[diet_type]
        output_emissions = user_input * conversion_factor
        # Here, insert_data() function should be modified to use Flask SQLAlchemy or another database connector compatible with Flask
        # insert_data(diet_type + '_emissions', user_input, output_emissions)

        return jsonify({'emissions': output_emissions})

    return "Invalid input.", 400



# Final run of the app
if __name__ == "__main__":
    app.run(debug=False)

    
