  
import numpy as np 
class CoordinateMapping3D:

    '''
    Defines a reference of coordinates by its origin respect to (0,0,0) and three ortogonal axis referred 
    to the cartsian axis. The class provides a method for transforming coordinates between reference frames
    for instance, from GPM (cartesian) to visage (rotated) or from  Petrel UI (y axis inverted) to any other.
    '''
    
    def __init__(self, axes = None, origin = None ):
        '''
        Creates a coordinate system with axis a1,a2,a3 referred to the cartesian. 
        Parameters: 
        axes = [[x1,y1,z1], [x2,y1,z1], [x3,y3,z3] ], i.e. the three orthogonal axis
        Origin: [o1,o2,o3] the origin of the coordinate frame respect to the universal (0,0,0)
        '''
    
        self.origin = np.array(origin) if origin is not None else np.array( [0.0,0.0,0.0] )
        self.a1 = np.array( axes[0] )  if axes   is not None else np.array( [1.0,0.0,0.0 ])
        self.a2 = np.array( axes[1] )  if axes   is not None else np.array( [0.0,1.0,0.0 ])
        self.a3 = np.array( axes[2] )  if axes   is not None else np.array( [0.0,0.0,1.0 ])
        self.DIMS = 3 
            
    def __repr__(self):
        
        os = '<CoordinateMApping>\n';
        os += " Origin: {} \n".format( self.origin )
        os += " Axis1:  {} \n".format( self.a1 )
        os += " Axis2:  {} \n".format( self.a2 )
        os += " Axis3:  {} \n".format( self.a3 )
        os += '<\CoordinateMApping>\n';
        
        return os;
    
    def __str__(self): return self.__repr__()
    
    def copy( self ):
        return CoordinateMapping3D( [self.a1,self.a2, self.a3], self.origin ) 

    def get_coefficients(self, c:'CoordinateMapping3D' ):  
        a1prime = c.a1;
        a2prime = c.a2;
        a3prime = c.a3;

        a11 = self.a1.dot( a1prime )
        a12 = self.a2.dot( a1prime)
        a13 = self.a3.dot( a1prime)
        a21 = self.a1.dot( a2prime)
        a22 = self.a2.dot( a2prime)
        a23 = self.a3.dot( a2prime)
        a31 = self.a1.dot( a3prime)
        a32 = self.a2.dot( a3prime)
        a33 = self.a3.dot( a3prime)

        return a11,a12,a13,a21,a22,a23,a31,a32,a33;


    
    def convert_to(self,source_xyz, c: 'CoordinateMapping3D' ):
        '''
        NOTE: different origins are not fully tested yet 
        
        Converts an array of coordinates (x1,y1,z1, x2,y2,z2, ...) to another coordinate system's 
        points (x1', y1',z1', ....)
        Both coordnate systems are defined by their own axes vectors respect to the cartesian and their 
        own origins 
        '''
    
        #difference in origin c2 - c1: vector from o1 to o2. [bo,b1,b2]
        rrprime = np.transpose( [c.origin - self.origin] ).reshape((1,3));
        npoints = int( source_xyz.size/self.DIMS);
        
        #rotation matrix
        aij = np.array ( [self.get_coefficients(c)] ).reshape((3,3))
        aij = np.vstack([aij, [0,0,0]] ) 
        
        traslated  = source_xyz.reshape(( npoints, 3 ) ) - rrprime
        
        aprime = traslated.reshape(( npoints, 3 ) )
        ones = np.ones( (npoints,1))
        aprime = np.c_[aprime, ones ]
        
        return (aprime.dot( aij )  ).flatten()
        
        #a11, a12, a13, a21, a22, a23, a31, a32, a33 = self.get_coefficients(c);
        #target_xyz = np.zeros( source_xyz.size );
        #count = int((source_xyz.size) / self.DIMS);
        #for n  in range(0,count):
        #    k = self.DIMS * n;
        #    target_xyz[k] = a11# * source_xyz[k] + a12 * source_xyz[k + 1] + a13 * source_xyz[k + 2] + rrprime[0];
            #target_xyz[k + 1] = a21 * source_xyz[k] + a22 * source_xyz[k + 1] + a23 * source_xyz[k + 2] + rrprime[1];
            #target_xyz[k + 2] = a31 * source_xyz[k] + a32 * source_xyz[k + 1] + a33 * source_xyz[k + 2] + rrprime[2];
        
    
    
    
    