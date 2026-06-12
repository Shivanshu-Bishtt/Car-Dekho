import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "cars.db")

CARS = [
    # Budget Hatchbacks
    ("Maruti Suzuki", "Alto K10", "VXi", 399000, "Petrol", 5, "Hatchback", 24.9, 2, "Peppy city hatchback with frugal engine and low running cost."),
    ("Maruti Suzuki", "WagonR", "ZXi Plus", 649000, "Petrol", 5, "Hatchback", 23.56, 3, "Tall-boy hatchback with spacious cabin and reliable powertrain."),
    ("Hyundai", "Grand i10 Nios", "Sportz", 749000, "Petrol", 5, "Hatchback", 20.7, 3, "Feature-rich budget hatchback with punchy engine and good ride."),
    ("Tata", "Tiago", "XZ Plus", 819000, "Petrol", 5, "Hatchback", 19.8, 4, "Safe and stylish hatchback with 5-star GNCAP rating."),
    ("Maruti Suzuki", "Swift", "ZXi Plus", 899000, "Petrol", 5, "Hatchback", 23.2, 3, "Sporty hatchback with eager engine and strong resale value."),
    ("Hyundai", "i20", "Asta", 1149000, "Petrol", 5, "Hatchback", 20.35, 3, "Premium hatchback with sunroof, BOSE audio, and refined cabin."),
    ("Tata", "Altroz", "XZ Plus", 1099000, "Petrol", 5, "Hatchback", 19.5, 5, "Safest hatchback in India with 5-star GNCAP and solid build."),

    # Sedans
    ("Honda", "Amaze", "V CVT", 1099000, "Petrol", 5, "Sedan", 18.6, 4, "Compact sedan with smooth CVT and comfortable long-distance ride."),
    ("Maruti Suzuki", "Dzire", "ZXi Plus", 999000, "Petrol", 5, "Sedan", 23.26, 3, "Best-selling compact sedan with excellent fuel economy."),
    ("Hyundai", "Verna", "SX IVT", 1599000, "Petrol", 5, "Sedan", 17.4, 3, "Feature-loaded mid-size sedan with ADAS and panoramic sunroof."),
    ("Honda", "City", "ZX CVT", 1699000, "Petrol", 5, "Sedan", 18.4, 4, "Legendary sedan with roomy cabin and segment-leading comfort."),
    ("Skoda", "Slavia", "Style TSI AT", 2099000, "Petrol", 5, "Sedan", 16.3, 5, "European-built sedan with 5-star GNCAP, sporty dynamics, and premium feel."),
    ("Toyota", "Camry", "Hybrid", 4850000, "Hybrid", 5, "Sedan", 19.16, 5, "Flagship hybrid sedan with serene cabin and self-charging powertrain."),

    # Compact SUVs
    ("Maruti Suzuki", "Brezza", "ZXi Plus AT", 1399000, "Petrol", 5, "SUV", 17.38, 4, "Refreshed compact SUV with 6 airbags and connected car tech."),
    ("Hyundai", "Venue", "SX Plus Turbo DCT", 1449000, "Petrol", 5, "SUV", 18.15, 3, "Trendy compact SUV with BlueLink connected tech and turbo engine."),
    ("Kia", "Sonet", "HTX Plus Diesel AT", 1599000, "Diesel", 5, "SUV", 24.1, 3, "Feature-rich compact SUV with diesel AT and ventilated seats."),
    ("Tata", "Nexon", "XZ Plus Dark", 1599000, "Petrol", 5, "SUV", 17.01, 5, "5-star GNCAP compact SUV with turbo engine and panoramic sunroof."),
    ("Nissan", "Magnite", "XV Turbo CVT", 1199000, "Petrol", 5, "SUV", 17.4, 4, "Value-packed compact SUV with turbo CVT and 360-degree camera."),
    ("Renault", "Kiger", "RXZ Turbo CVT", 1199000, "Petrol", 5, "SUV", 18.2, 3, "Stylish compact SUV with large touchscreen and efficient turbo engine."),

    # Mid-size SUVs
    ("Hyundai", "Creta", "SX Opt Diesel AT", 1999000, "Diesel", 5, "SUV", 18.42, 3, "India's best-selling mid-size SUV with ADAS and panoramic sunroof."),
    ("Kia", "Seltos", "HTX Plus Diesel AT", 2099000, "Diesel", 5, "SUV", 18.23, 3, "Premium mid-size SUV with Bose audio, HUD, and robust diesel engine."),
    ("Maruti Suzuki", "Grand Vitara", "Alpha Hybrid", 1999000, "Hybrid", 5, "SUV", 27.97, 3, "Strong hybrid SUV with best-in-segment fuel efficiency."),
    ("Toyota", "Urban Cruiser Hyryder", "V Hybrid", 2099000, "Hybrid", 5, "SUV", 27.97, 4, "Reliable hybrid SUV with Toyota's proven self-charging tech."),
    ("Tata", "Harrier", "XZA Plus Dark", 2699000, "Diesel", 5, "SUV", 16.35, 4, "Bold design with OMEGA Arc platform, panoramic sunroof, and diesel AT."),
    ("Volkswagen", "Taigun", "GT Plus TSI AT", 2099000, "Petrol", 5, "SUV", 16.35, 5, "German-engineered compact SUV with 5-star GNCAP and DSG gearbox."),
    ("Skoda", "Kushaq", "Monte Carlo TSI AT", 1999000, "Petrol", 5, "SUV", 16.1, 5, "Sporty Monte Carlo edition with 5-star safety and sporty styling."),

    # Large & Premium SUVs
    ("Tata", "Safari", "XZA Plus Dark", 2899000, "Diesel", 7, "SUV", 14.08, 4, "7-seat flagship SUV with panoramic sunroof and premium interiors."),
    ("MG", "Hector Plus", "Sharp Pro Diesel", 2499000, "Diesel", 7, "SUV", 15.07, 3, "6/7-seat smart SUV with 14-inch touchscreen and i-SMART tech."),
    ("Mahindra", "XUV700", "AX7 Diesel AWD AT", 3199000, "Diesel", 7, "SUV", 15.17, 5, "Feature-loaded 7-seat SUV with ADAS, AdrenoX, and 5-star safety."),
    ("Jeep", "Compass", "Limited Plus Diesel AT", 3499000, "Diesel", 5, "SUV", 15.35, 4, "Italian-designed SUV with premium cabin and capable off-road kit."),
    ("Toyota", "Fortuner", "Legender 4WD AT", 4799000, "Diesel", 7, "SUV", 10.02, 4, "Legendary 7-seat SUV with robust 4WD and strong resale value."),

    # MPVs
    ("Maruti Suzuki", "Ertiga", "ZXi Plus AT", 1349000, "Petrol", 7, "MPV", 19.34, 3, "Best-selling 7-seat MPV with smooth AT and efficient CNG option."),
    ("Kia", "Carens", "Luxury Plus Diesel DCT", 1899000, "Diesel", 7, "MPV", 19.87, 3, "Feature-rich 6/7-seat MPV with ventilated seats and ADAS."),
    ("Toyota", "Innova Crysta", "GX Diesel MT", 2099000, "Diesel", 7, "MPV", 11.26, 4, "Workhorse 7-seat MPV with legendary Toyota reliability and spacious cabin."),
    ("Toyota", "Innova HyCross", "ZX Hybrid", 3499000, "Hybrid", 7, "MPV", 21.1, 4, "Premium hybrid MPV with strong hybrid system and luxurious cabin."),
    ("Renault", "Triber", "RXZ AT", 849000, "Petrol", 7, "MPV", 18.58, 4, "Affordable 7-seat MPV with modular seating and city-friendly size."),

    # EVs
    ("Tata", "Nexon EV", "Max XZ Plus LR", 1999000, "EV", 5, "SUV", 0.0, 5, "430 km range EV with fast charging, connected tech, and 5-star safety."),
    ("Tata", "Tiago EV", "XZ Plus Long Range", 1299000, "EV", 5, "Hatchback", 0.0, 4, "Affordable EV hatchback with 315 km range and peppy performance."),
    ("MG", "ZS EV", "Excite Pro", 2499000, "EV", 5, "SUV", 0.0, 3, "461 km range electric SUV with panoramic sunroof and connected features."),
    ("Hyundai", "Creta Electric", "Excellence", 2999000, "EV", 5, "SUV", 0.0, 4, "473 km range electric with ADAS, V2L, and premium cabin finish."),
    ("BYD", "Atto 3", "Standard", 3399000, "EV", 5, "SUV", 0.0, 5, "521 km range EV with distinctive interior and 5-star NCAP safety."),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cars")
    cur.execute("""
        CREATE TABLE cars (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            make        TEXT NOT NULL,
            model       TEXT NOT NULL,
            variant     TEXT NOT NULL,
            price       INTEGER NOT NULL,
            fuel_type   TEXT NOT NULL,
            seats       INTEGER NOT NULL,
            body_type   TEXT NOT NULL,
            mileage_kmpl REAL NOT NULL,
            safety_rating INTEGER NOT NULL,
            summary     TEXT NOT NULL
        )
    """)
    cur.executemany(
        "INSERT INTO cars (make, model, variant, price, fuel_type, seats, body_type, mileage_kmpl, safety_rating, summary) VALUES (?,?,?,?,?,?,?,?,?,?)",
        CARS,
    )
    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
    conn.close()
    return count


def get_all_cars():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM cars").fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    n = init_db()
    print(f"cars.db created — {n} cars inserted.")
