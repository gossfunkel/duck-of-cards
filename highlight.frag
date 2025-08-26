#version 450

// pass value into shader from main code
uniform vec2 resolution;
mediump vec2 gl_PointCoord; //fragment position within a point (point rasterization only) 

//uniform sampler2D p3d_Texture0;

// input 
in vec2 texcoord;
in vec4 p3d_Color;

// out to screen
out vec4 p3d_FragColor;

void main() {
	// simply add brightness to fragment
	vec3 col = p3d_FragColor.xyz + vec3(0.1,0.1,0.1);
	p3d_FragColor = vec4(col,1.);

}
