from flask import Flask, jsonify, request, Response
import os

import poliastro
from astropy.units.core import PrefixUnit
import importlib
from poliastro.twobody import Orbit
from flask_cors import cross_origin, CORS


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.debug = True
# CORS(app, resources=r'/orbit-plot')

@app.route('/')
def hello_world():
    target = os.environ.get('TARGET', 'World')
    return 'Hello {}!\n'.format(target)

@app.route('/orbit', methods=['GET', 'POST'])
@cross_origin(origin='*', allow_headers=['Content-Type'])
def orbit_example():
    if request.method == 'POST':
        if request.is_json:

            # load JSON data
            req = request.get_json()

            # getting the body from JSON and importing it from poliastro
            body = req.get("body")
            import_path = "poliastro.bodies"
            bodies = importlib.import_module(import_path)
            body = getattr(bodies, body)

            # loading position magnitude and unit and unifying it
            position_value = req.get("position").get("value")
            position_unit = req.get("position").get("unit")
            position_unit = PrefixUnit(position_unit)
            r = position_value * position_unit

            # loading velocity magnitude and unit and unifying it
            velocity_value = req.get("velocity").get("value")
            velocity_unit = req.get("velocity").get("unit")
            velocity_unit = velocity_unit.split("/")
            velocity_unit = list(map(PrefixUnit, velocity_unit))
            v = velocity_value * velocity_unit[0] / velocity_unit[1]

            # Calculating Orbit
            final_orbit = Orbit.from_vectors(body, r, v)

            pericenter_radius = final_orbit.r_p.value
            apocenter_radius = final_orbit.r_a.value
            inclination = final_orbit.inc.value
            reference_frame = str(final_orbit.frame)
            attractor = str(final_orbit.attractor)
            epoch = final_orbit.epoch.value

            return jsonify(pericenter_radius=pericenter_radius, apocenter_radius=apocenter_radius, inclination=inclination, reference_frame=reference_frame[1:-1], attractor=attractor, epoch=epoch)

@app.route('/orbit-plot', methods=['GET', 'POST'])
@cross_origin(origins='*', allow_headers=['Content-Type'])
def orbit_plot():
    if request.is_json:

        # load JSON data
        req = request.get_json()

        # getting the body from JSON and importing it from poliastro
        body = req.get("body")
        import_path = "poliastro.bodies"
        bodies = importlib.import_module(import_path)
        body = getattr(bodies, body)

        # loading position magnitude and unit and unifying it
        position_value = req.get("position").get("value")
        position_unit = req.get("position").get("unit")
        position_unit = PrefixUnit(position_unit)
        r = position_value * position_unit

        # loading velocity magnitude and unit and unifying it
        velocity_value = req.get("velocity").get("value")
        velocity_unit = req.get("velocity").get("unit")
        velocity_unit = velocity_unit.split("/")
        velocity_unit = list(map(PrefixUnit, velocity_unit))
        v = velocity_value * velocity_unit[0] / velocity_unit[1]

        # Calculating Orbit
        final_orbit = Orbit.from_vectors(body, r, v)
        final_orbit = final_orbit.plot(interactive=True, use_3d=True)
        print(final_orbit['data'],"\n \n \n \n",final_orbit['layout'])
        # data = dict(final_orbit['data'])
        # layout = dict(final_orbit['layout'])
        b = final_orbit.to_json()
        resp = Response(b)

        resp.headers['Content-Type'] = 'application/json'
        # resp.headers['Content-Transfer-Encoding'] = 'base64'
        # resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
