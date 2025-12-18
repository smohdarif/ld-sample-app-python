import os
from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask_cors import CORS
import ldclient
from ldclient.config import Config
from dotenv import load_dotenv

load_dotenv()

with open("static/js/keys.js", "w") as f:
    f.write('const clientKey = "' + os.environ["LD_CLIENT_KEY"] + '";')

app = Flask(__name__)
CORS(app)


class change_tracker:
    def __call__(self, changed):
        print(
            "Flag key: "
            + str(changed.key)
            + ", Old value: "
            + str(changed.old_value)
            + ", New value: "
            + str(changed.new_value)
        )


changer = change_tracker()

ldclient.set_config(Config(os.environ["LD_SDK_KEY"]))

if ldclient.get().is_initialized():
    print("SDK successfully initialized!")
else:
    print("SDK failed to initialize")

mycontext = ldclient.Context.from_dict(
    {
        "kind": "multi",
        "user": {
            "key": "user-018e7bd4-ab96-782e-87b0-b1e32082b481",
            "name": "Miriam Wilson",
            "language": "en",
            "tier": "premium",
            "userId": "mwilson",
            "role": "developer",
            "email": "miriam.wilson@example.com",
        },
        "device": {
            "key": "device-018e7bd4-ab96-782e-87b0-b1e32082b481",
            "os": "macOS",
            "osVersion": "15.6",
            "model": "MacBook Pro",
            "manufacturer": "Apple",
        },
    }
)

ldclient.get().flag_tracker.add_flag_value_change_listener(
    "coffee-promo-1", mycontext, changer
)
ldclient.get().flag_tracker.add_flag_value_change_listener(
    "coffee-promo-2", mycontext, changer
)
ldclient.get().flag_tracker.add_flag_value_change_listener(
    "ziphq", mycontext, changer
)


@app.route("/")
def show_page():
    current_route_rule = str(request.url_rule)
    home_page_slider = ldclient.get().variation(
        "release-home-page-slider", mycontext, False
    )
    coffee_promo_1 = ldclient.get().variation("coffee-promo-1", mycontext, False)
    coffee_promo_2 = ldclient.get().variation("coffee-promo-2", mycontext, False)
    ziphq_enabled = ldclient.get().variation("ziphq", mycontext, False)
    retval = make_response(
        render_template(
            "index.html",
            current_route_rule=current_route_rule,
            home_page_slider=home_page_slider,
            coffee_promo_1=coffee_promo_1,
            coffee_promo_2=coffee_promo_2,
            ziphq_enabled=ziphq_enabled,
        )
    )
    return retval


@app.route("/about")
def show_about():
    current_route_rule = str(request.url_rule)
    retval = make_response(
        render_template("about.html", current_route_rule=current_route_rule)
    )
    return retval


@app.route("/products")
def show_products():
    current_route_rule = str(request.url_rule)
    retval = make_response(
        render_template("products.html", current_route_rule=current_route_rule)
    )
    return retval


@app.route("/contact")
def show_contact():
    current_route_rule = str(request.url_rule)
    retval = make_response(
        render_template("contact.html", current_route_rule=current_route_rule)
    )
    return retval


@app.route("/api/banner")
def home_page_banner():
    primary_banner = ldclient.get().variation(
        "banner-text", mycontext, "No banner text found!"
    )
    return {"primaryBanner": primary_banner}


@app.route("/api/ziphq")
def ziphq_status():
    """API endpoint to check ZipHQ feature flag status"""
    ziphq_enabled = ldclient.get().variation("ziphq", mycontext, False)
    return {
        "flag": "ziphq",
        "enabled": ziphq_enabled,
        "context": {
            "user": mycontext.get("user").key,
            "name": mycontext.get("user").get("name")
        }
    }


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
