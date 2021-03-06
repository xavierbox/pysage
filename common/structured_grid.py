import pandas as pd 
import numpy as np 

from .coordinate_map import CoordinateMapping3D as CoordinateMapping3D 
from .structured_base import StructuredBase as StructuredBase 

class StructuredGrid( StructuredBase ):
    
    def __init__( self, ncols:int, nrows:int, nlayers:int, extent:'np.array2d', reference:'CoordinateMapping3D'=None ):
        
        super().__init__( ncols, nrows, nlayers, extent, reference )
        
        #list of numpy arrays 
        self._zvalues  = [np.zeros(self.nodes_per_layer) for n in range(0,self.nlayers)] #klayers
        self._horizons = [np.zeros(self.nodes_per_layer) for n in range(0,self.nlayers)] #horizons 
        
    def copy( self ):
        s = StructuredGrid( self.ncols, self.nrows, self.nsurfaces, self.length, self.reference )
        s._zvalues  = self._zvalues.copy()
        s._horizons = self._horizons.copy()
        return s
          
    @property
    def is_flipped( self ):
        '''
        Returns true if the surface 0 is the shallower otherwise returns False
        '''
        if len(self._zvalues)>=2:
            z0 = self._zvalues[0]
            z1 = self._zvalues[ len(self._zvalues) -1 ]
            if sum(z0)/len(z0) > sum(z1)/len(z1): return True
            
        return False 
        
    @property 
    def depths( self ): return self._zvalues;

    def get_local_depths(self, nk:int)->np.ndarray: return self._zvalues[nk]

    def _add_surfaces_if_needed(self,surface_index:int):
        
        while surface_index >= len(self._zvalues): 
            self._zvalues.append(np.zeros(self.nodes_per_layer))
        self._node_count[2] = 1 + surface_index;
        
    def set_num_surfaces(self, nz:int ):
        self._add_surfaces_if_needed(nz-1);
    
    def set_z_values(self,surface_index:int, values):
        
        self._add_surfaces_if_needed(surface_index)        
        nodes_per_layer = self.nodes_per_layer 
    
        if isinstance(values,list):
            self._zvalues[surface_index]= np.array( values, dtype = float  )
            
        elif isinstance(values, np.ndarray):
            self._zvalues[surface_index]= values.copy()
            
        elif isinstance(values, (int, float, np.float64,np.float32 )):
            self._zvalues[surface_index]= np.array( nodes_per_layer*[values], dtype=float)
            
        else:
            raise ValueError('Cannot create z coordinates with an object of type ', type(values) )
            
    def displace_all_nodes( self,displacement ):
        
        if isinstance( displacement,(int,float, np.float64, np.float32)):
            d = float( displacement )
            for n in range(0, self.nlayers):
                self._zvalues[n]  = self._zvalues[n] + d 
                
        elif isinstance(displacement,list):
            for n in range(0, self.nlayers):self._zvalues[n]  = self._zvalues[n] + np.array( d )
            
            
        elif isinstance(displacement, np.ndarray):
            for n in range(0, self.nlayers):self._zvalues[n] = self._zvalues[n] + d

        else : 
            raise ValueError('Cannot displace the nodes with an object of type ', type(displacement) )
                        
           
    def get_local_coordinates_vectors( self, surface_index:int ):

        ret = 3*self.nodes_per_layer*[0]
        spacing = self.horizontal_spacing;
        z = self._zvalues[surface_index];
        counter = -1;

        for nj in range( 0, self.nrows):
            x2 = spacing[1] * nj;
            for ni in range( 0, self.ncols):
                counter+=1
                #ret[counter] = np.array( [spacing[0] * ni, x2, z[counter]] ) ;
                ret[3*counter] = spacing[0] * ni
                ret[3*counter+1]=x2
                ret[3*counter+2]= z[counter] ;
                
            
        return np.array(ret).reshape( (self.nodes_per_layer,3) )
    

    def get_all_local_coordinates( self ):
        
        #fixme use list comprehensions 
        all_data =[]
        for n in range(0, self.nsurfaces):
            xyz = list(self.get_local_coordinates_vectors( n ).flatten())
            all_data.extend( xyz )
        
        return np.array( all_data )
    
    #only non-inverted grids. 
    def get_node_depths_from_top( self ):
        
        '''
        Returns the vertical depth (positive) of each node from the top of the grid
        
        zop[n] = z[n]
        
        Tested 
        '''
        zvalues = self._zvalues; 
        model_top = zvalues[self.nsurfaces - 1];

        ret = np.zeros( self.num_nodes );
        counter = -1 
        
        for n in range( 0, self.nsurfaces ):
            depth = model_top - zvalues[n]
            n1 = n * self.nodes_per_layer
            n2 = n1 + self.nodes_per_layer
            
            ret[n1:n2] = depth 
            
        return ret.reshape( (self.nsurfaces,self.nodes_per_layer) ) 

    
    def get_pinched_elements( self, pinchout_tolerance:float  = 1.0e-6):
        
        '''
        This is used to create rcn files for pinched-out elements.
        
        TESTED ok 
        '''
        
        element_pinched_count = self.num_cells * [0]
        node_connections = {}
        nodes_per_surface = self.nodes_per_layer 
        
        for k1 in range( 0, self.nsurfaces-1):
            
            k2 = k1 + 1;
            heights_below = self.get_local_depths( k1 );
            heights_above = self.get_local_depths( k2 );

            difference = heights_above - heights_below;
        
            for node in range( 0, difference.size ):
                if abs(difference[node]) < pinchout_tolerance:
                    
                    node1 = nodes_per_surface * k1 + node;
                    node2 = node1 + nodes_per_surface;
                    element_indices = self.get_element_indices_above_node( node1 );

                    for ele in element_indices:
                        element_pinched_count[ele] = element_pinched_count[ele] + 1;
                    
                    node_connections[node1] = node2;
                    
        return element_pinched_count, node_connections
    

    