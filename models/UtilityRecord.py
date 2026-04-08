class UtilityRecord:
    def __init__(self, service_type, prev_reading_day, curr_reading_day, tariff_day, water_constant = 0, prev_reading_night = 0, curr_reading_night = 0, tariff_night = 0):
        self.service_type = service_type
        self.prev_reading_day = prev_reading_day
        self.curr_reading_day = curr_reading_day
        self.tariff_day = tariff_day
        self.prev_reading_night = prev_reading_night
        self.curr_reading_night = curr_reading_night
        self.tariff_night = tariff_night
        self.water_constant = water_constant
        self.total_to_pay = self.calculate_total_to_pay()

    def calculate_total_to_pay(self):
        day = ((self.curr_reading_day - self.prev_reading_day) * self.tariff_day)
        night = ((self.curr_reading_night - self.prev_reading_night) * self.tariff_night)
        return day + night + self.water_constant
