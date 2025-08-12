#version 300

uniform mat4 p3d_ModelViewProjectionMatrix;

// vertex inputs
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

// to fragment
out vec2 texcoord;

void main () {
	gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
	texcoord = p3d_MultiTexCoord0;

	// define anchor points of curve
	// 2/3 of the way along the tile

	// define curve
	// like a bezier maybe?

	// pass to fragment shader
	// texcoord = ???;
}
