#! /usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import sys
import ctypes
import math
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
from OpenGL.arrays import vbo
from OpenGL.GL import *
from OpenGL.GL import shaders
import random

terrain_size = 8

vertex_code = """
        uniform mat4 projection;
        uniform mat4 model;
        uniform mat4 view;
        uniform float[""" + str(terrain_size+1) + """][""" + str(terrain_size+1) + """] heightMap;
        void main() {
            gl_Position = projection * model * gl_Vertex;
        }"""

fragment_code = """
        void main() {
            gl_FragColor = vec4( 0, 1, 0, 1 );
        }"""



def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glUseProgram(program)
    
    gl.glEnableClientState(GL_VERTEX_ARRAY);
    terrain_vbo.bind()
    gl.glVertexPointerf( terrain_vbo )
    
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(terrain))
    
    terrain_vbo.unbind()
    gl.glDisableClientState(GL_VERTEX_ARRAY)
    
    glut.glutSwapBuffers()

def reshape(width,height):
    setProjection(60,width,height)
    gl.glViewport(0, 0, width, height)

def keyboard( key, x, y ):
    if key == '\033':
        sys.exit( )

def getRotationMatrix(x,y,z):
    x = math.radians(x)
    y = math.radians(y)
    z = math.radians(z)
    
    x_mat = np.matrix([[1.0,         0.0,          0.0, 0.0], 
                       [0.0, math.cos(x), -math.sin(x), 0.0], 
                       [0.0, math.sin(x),  math.cos(x), 0.0], 
                       [0.0,         0.0,          0.0, 1.0]], np.float32)

    y_mat = np.matrix([[ math.cos(y), 0.0, math.sin(y), 0.0], 
                       [         0.0, 1.0,         0.0, 0.0], 
                       [-math.sin(y), 0.0, math.cos(y), 0.0], 
                       [         0.0, 0.0,         0.0, 1.0]], np.float32)

    z_mat = np.matrix([[math.cos(z), -math.sin(z), 0.0, 0.0], 
                       [math.sin(z),  math.cos(z), 0.0, 0.0], 
                       [        0.0,          0.0, 1.0, 0.0], 
                       [        0.0,          0.0, 0.0, 1.0]], np.float32)

    result_mat = z_mat * y_mat * x_mat

    return result_mat
    

def setProjection(fov,width,height):
    fov = math.radians(fov)
    f = 1.0/math.tan(fov/2.0)
    zF = 100
    zN = 0.1
    a = (float(width)/height) 

    projMat = np.array([f/a, 0, 0 ,0,
                         0, f, 0 ,0,
                         0, 0, (zF+zN)/(zN-zF) ,-1.0,
                         0, 0, 2.0*zF*zN/(zN-zF) ,0], np.float32)

    modelMat = np.identity(4,np.float32)

    translation = np.matrix([[1.0, 0.0, 0.0, 0.0], 
                             [0.0, 1.0, 0.0, 0.0], 
                             [0.0, 0.0, 1.0, 0.0], 
                             [-0.5, -0.5, 0, 1.0]], np.float32)

    scale = np.matrix([[0.75, 0.0, 0.0, 0.0], 
                       [0.0, 0.75, 0.0, 0.0], 
                       [0.0, 0.0, 0.75, 0.0], 
                       [0.0, 0.0, 0.0, 1.0]], np.float32)

    view_translation = np.matrix([[1.0, 0.0, 0.0, 0.0], 
                                  [0.0, 1.0, 0.0, 0.0], 
                                  [0.0, 0.0, 1.0, 0.0], 
                                  [0, 0, -1, 1.0]], np.float32)

    modelMat = modelMat * translation * scale * getRotationMatrix(0,0,45) * getRotationMatrix(75,0,0) * view_translation

    gl.glUseProgram(program)

    loc = gl.glGetUniformLocation(program, "model")
    gl.glUniformMatrix4fv(loc, 1, GL_FALSE, np.array(modelMat).flatten())

    loc = gl.glGetUniformLocation(program, "projection")
    gl.glUniformMatrix4fv(loc, 1, GL_FALSE, projMat)


# GLUT init
# --------------------------------------
glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('Hello world!')
glut.glutReshapeWindow(800,600)
glut.glutReshapeFunc(reshape)
glut.glutDisplayFunc(display)
glut.glutKeyboardFunc(keyboard)

# Build data
# --------------------------------------
#data = np.zeros(4, [("position", np.float32, 2),
#                    ("color",    np.float32, 4)])
#data['color']    = [ (1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1) ]
#data['position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]

# Build & activate program
# --------------------------------------

# Request a program and shader slots from GPU
program  = gl.glCreateProgram()
vertex   = gl.glCreateShader(gl.GL_VERTEX_SHADER)
fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

# Set shaders source
gl.glShaderSource(vertex, vertex_code)
gl.glShaderSource(fragment, fragment_code)

# Compile shaders
gl.glCompileShader(vertex)
gl.glCompileShader(fragment)

# Attach shader objects to the program
gl.glAttachShader(program, vertex)
gl.glAttachShader(program, fragment)

# Build program
gl.glLinkProgram(program)

# Get rid of shaders (no more needed)
gl.glDetachShader(program, vertex)
gl.glDetachShader(program, fragment)

# Make program the default program
#gl.glUseProgram(program)


# Build buffer
# --------------------------------------

# Request a buffer slot from GPU
#buffer = gl.glGenBuffers(1)

# Make this buffer the default one
#gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)

# Upload data
#gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)


# Bind attributes
# --------------------------------------

#stride = data.strides[0]
#offset = ctypes.c_void_p(0)
#loc = gl.glGetAttribLocation(program, "position")
#gl.glEnableVertexAttribArray(loc)
#gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
#gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, stride, offset)

#offset = ctypes.c_void_p(data.dtype["position"].itemsize)
#loc = gl.glGetAttribLocation(program, "color")
#gl.glEnableVertexAttribArray(loc)
#gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
#gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, False, stride, offset)

# Bind uniforms
# --------------------------------------
#loc = gl.glGetUniformLocation(program, "scale")
#gl.glUniform1f(loc, 1.0)

gl.glEnableClientState(GL_VERTEX_ARRAY);

terrain = np.empty([((terrain_size)*(terrain_size)*6), 3],'f')

##terrain = np.array([[0.0,0.0,0.0],
##                   [0.0,1.0,0.0],
##                   [1.0,0.0,0.0]])

for x in xrange(terrain_size):
    for y in xrange(terrain_size):
        offset = (terrain_size*x+y)*6
        terrain[offset+0] = [x,y,0]
        terrain[offset+1] = [x+1,y,0]
        terrain[offset+2] = [x,y+1,0]
        terrain[offset+3] = [x,y+1,0]
        terrain[offset+4] = [x+1,y,0]
        terrain[offset+5] = [x+1,y+1,0]

terrain = np.divide(terrain,float(terrain_size))

terrain_vbo = vbo.VBO(terrain)

print terrain

height_loc = gl.glGetUniformLocation(program, "heightMap")

#setProjection(60,1,1)


# Enter mainloop
# --------------------------------------
glut.glutMainLoop()
