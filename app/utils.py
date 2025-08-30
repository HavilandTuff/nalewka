class VolumeConverter:
    """Utility class for volume conversions"""

    @staticmethod
    def to_ml(value, unit):
        """Convert any volume unit to milliliters"""
        if unit == "l":
            return value * 1000
        elif unit == "oz":
            return value * 29.5735  # fluid ounces to ml
        elif unit == "cup":
            return value * 236.588
        elif unit == "tsp":
            return value * 4.92892
        elif unit == "tbsp":
            return value * 14.7868
        return value  # assume ml if unknown

    @staticmethod
    def from_ml(value_ml, target_unit):
        """Convert milliliters to target unit"""
        if target_unit == "l":
            return value_ml / 1000
        elif target_unit == "oz":
            return value_ml / 29.5735
        elif target_unit == "cup":
            return value_ml / 236.588
        elif target_unit == "tsp":
            return value_ml / 4.92892
        elif target_unit == "tbsp":
            return value_ml / 14.7868
        return value_ml  # return ml if unknown
