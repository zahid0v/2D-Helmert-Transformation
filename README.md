# 2D Helmert Transformation
Streamlit app to transform coordinates from one rectangular source coordinate system to another target coordinate system.  
The 2D Helmert transformation is the most common planar transformation method in surveying. The shape of objects is not distorted.  

The transformation consists of 4 parameters:
            
$Y_0:$&ensp;Translation (shift) from source into target system in the y-axis direction   
$X_0:$ Translation (shift) from source into target system in the x-axis direction  
$k:$ Scale  
$\theta:$ Rotation

Two or more points with known coordinates in both source and target system must be known to determine the transformation parameters.
If more than 2 common points are given, a standard deviation and residuals of the common points can be calculated.

for problems and suggestions contact: s.engelhard@gmx.net