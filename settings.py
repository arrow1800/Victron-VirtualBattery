CHARGE_VOLTAGE = 2.48                                   # Constant voltage charge = this value * nr. of cells
MAX_CELL_VOLTAGE = 2.55                                 # If reached by 1-st cell, the charger voltage is clamped to the measured value
DISCHARGE_VOLTAGE = 2.1                                 # If reached, discharge current set to zero
MIN_CELL_VOLTAGE = 2                                    # If reached, discharge current set to zero

MAX_CHARGE_CURRENT = 200                                # Max. charge current at normal conditions
MAX_DISCHARGE_CURRENT = 200                             # Max. discharge current at normal conditions

MAX_CHARGE_CURRENT_ABOVE_CV1 = 50                       # Reduction of charge current if the max. cell voltage reaches CV1
CV1 = 2.45
MAX_CHARGE_CURRENT_ABOVE_CV2 = 10                       # Reduction of charge current if the max. cell voltage reaches CV2
CV2 = 2.52