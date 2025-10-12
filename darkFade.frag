#version 450

in vec2 texcoord;
uniform float range;

// out to screen
out vec4 p3d_FragColor;

void main() {
	// generate a black fade from the bottom of the screen
	p3d_FragColor = vec4(0.,0.,0.02,0.9-texcoord.y*range);

}