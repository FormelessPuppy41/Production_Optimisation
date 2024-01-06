import pyomo
import pyomo.opt
import pyomo.environ as pyo
from icecream import ic

ic("Show set names outside of model.")

# Create pyo.Set instances, with names
my_set1 = pyo.Set(initialize=[1,2,3], name='Set1')
my_set2 = pyo.Set(initialize=[7,8,9], name='Set2')

# Print names
ic(my_set1.name) # Works correctly
ic(my_set2.name) # Works correctly

ic(list(my_set1.value))
######
# Combine the two pyo.Set's to get a single multi dimensional pyo.Set
ic('Combine sets')
my_set3 = pyo.Set(initialize=my_set1 * my_set2) # Works correctly
ic(element for element in my_set3) # Results in error.

# Indicate name of the two dimensions
my_set3.name = (my_set1.name, my_set2.name) # Works correctly

# Retrieve name of dimensions of set.
ic(my_set3.getname()) # Works correctly


ic("# ----------------------------------------------#")


ic("Show set names inside of model")

# Create model
model = pyo.ConcreteModel()

# Create pyo.Set instances with names INSIDE of the model.
model.my_set1 = pyo.Set(initialize=[1,2,3], name='Set1')
model.my_set2 = pyo.Set(initialize=[7,8,9], name='Set2')

# Print names
ic(model.my_set1.name) # prints my_set1 instead of Set1
ic(model.my_set2.name) # prints my_set2 instead of Set2

# Combine the two pyo.Set's to get a single multi dimensional pyo.Set
ic("Combine sets")
model.my_set3 = model.my_set1 * model.my_set2 

ic(list(model.my_set3))

# Indicate name of the two dimensions 
model.my_set3.name = (model.my_set1.name, model.my_set2.name) # Here it indicates an error, namely: File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/pyomo/core/base/component.py", line 671, in name. \n raise ValueError( ValueError: The .name attribute is not settable when the component is assigned to a Block. Triggered by attempting to set component 'my_set3' to name '('my_set1', 'my_set2')'

# Retrieve name of dimensions of set.
ic(model.my_set3.getname())






"""
my_set4 = pyo.Set(
    initialize=my_set1 * my_set2
    )
ic(my_set4.getname())

my_set4.name = my_set1.name, my_set2.name
ic(my_set4.getname())
"""
#ic(my_set3, tuple(my_set3.name.strip('()').split(',')))
#var1 = pyo.Var(my_set3, domain=pyo.Binary)
