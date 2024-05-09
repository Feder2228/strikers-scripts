import os, struct, math, shutil, glob, re

# Function to read floats of the vertex data section
# I made this when I didn't know anything else about how the vertex section works
def read_vertex_floats(rlg):
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    #print( byte_hex_str(data) )

    #find the section
    location = data.find(b'\x00\x01\xb0\x06')
    print( hex(location) )

    floats = []
    rlg.seek( location+8 ,0)
    while rlg.tell() < file_size:
        bytes = rlg.read(4)
        f = struct.unpack( '!f', bytes )[0]
        if( math.isnan(f) or math.isinf(f) ):
            break
        floats.append(f)
    print(floats[:10])

# Function to read the vertices of a rlg file
def get_vertices_from_rlg(rlg, vertex_attributes):
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    #print( byte_hex_str(data) )

    #find the section
    location = data.find(b'\x00\x01\xb0\x06')

    rlg.seek( location+4 ,0)
    section_size = int.from_bytes( rlg.read(4), "big" )
    start_of_data = rlg.tell()
    group = 0
    last_0x4 = 0
    unknown_0x4 = None
    a = []
    while rlg.tell() < start_of_data+section_size:
        current_byte = rlg.tell() - start_of_data
        stride = 4
        # check vertex attribute offset
        for i in vertex_attributes:
            if( i['offset'] <= current_byte ):
                stride = i['stride']
                unknown_0x4 = i['0x4']                
        if(last_0x4 == 0xb0 and unknown_0x4 == 0x67):
            group += 1
        last_0x4 = unknown_0x4

        new_vector = []
        for i in range(0, stride//4):
            bytes = rlg.read(4)
            f = struct.unpack( '!f', bytes )[0]
            new_vector.append(f)
        a.append( {
            "offset" : current_byte,
            "type" : unknown_0x4, 
            "group" : group,
            "values" : new_vector
        } )
    
    # fliter only the vertices we need
    vertices = []

    for i in a:
        if( i['type'] == 0x67 ):
            vertices.append( i )
    return vertices


def read_vertex_attribute(rlg):
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    #print( byte_hex_str(data) )

    #find the section
    location = data.find(b'\x00\x01\xb0\x05')

    # read data
    rlg.seek( location+4 ,0)
    section_size_b = rlg.read(4)
    section_size = int.from_bytes( section_size_b, "big" )
    a = []
    while rlg.tell() < location+8+section_size:
        offset = int.from_bytes( rlg.read(4), "big" )
        unknown_0x4 = int.from_bytes( rlg.read(1), "big" )
        stride = int.from_bytes( rlg.read(1), "big" )
        unknown_0x6 = int.from_bytes( rlg.read(2), "big" )

        a.append( {
            "offset" : offset,
            "0x4" : unknown_0x4, # 67 fe cc ed 52 c0 d6 d7 d4 b0
            "stride" : stride,
            "0x6" : unknown_0x6
        } )
    return a


def read_mesh_data(rlg, verbose = False):
    # Get the rlg filename without extension
    filename = os.path.basename(rlg.name)
    print("Reading mesh data of: " +filename)
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    #print( byte_hex_str(data) )

    #find the section
    location = data.find(b'\x00\x01\xb0\x04')

    # get section size
    rlg.seek( location+4 ,0)
    section_size = int.from_bytes( rlg.read(4), "big" )
    start_of_data = rlg.tell()

    # read data
    a = []
    while rlg.tell() < start_of_data+section_size:
        index_start_offset = int.from_bytes( rlg.read(4), "big" )
        index_flags = int.from_bytes( rlg.read(4), "big" )
        face_type = int.from_bytes( rlg.read(1), "big" )
        attribute_count = int.from_bytes( rlg.read(1), "big" )
        unknown_0x0a = int.from_bytes( rlg.read(4), "big" )
        material_hash_id = int.from_bytes( rlg.read(4), "big" )
        mesh_hash_id = int.from_bytes( rlg.read(4), "big" )
        unknown_0x16 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x1a = int.from_bytes( rlg.read(4), "big" )
        material_offset = int.from_bytes( rlg.read(4), "big" )
        unknown_0x22 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x26 = int.from_bytes( rlg.read(4), "big" )
        unknown_0x2a = int.from_bytes( rlg.read(6), "big" )

        if(verbose):
            a.append( { 
                "index_start_offset" : index_start_offset,
                "index_count" : index_flags & 0xffffff,
                "index_format" : index_flags >> 24,
                "face_type" : face_type,
                "attribute_count" : attribute_count,
                "0x0a" : unknown_0x0a,
                "material_hash_id" : material_hash_id,
                "0x16" : unknown_0x16,
                "0x1a" : unknown_0x1a,
                "mesh_hash_id" : mesh_hash_id,
                "material_offset" : material_offset,
                "0x22" : unknown_0x22,
                "0x26" : unknown_0x26,
                "0x2a" : unknown_0x2a,
            }   
            )
        else:
            a.append( { 
                "index_start_offset" : index_start_offset,
                "index_count" : index_flags & 0xffffff,
                "index_format" : index_flags >> 24,
                "face_type" : face_type,
                "attribute_count" : attribute_count,
                "material_hash_id" : material_hash_id,
                "mesh_hash_id" : mesh_hash_id,
                "material_offset" : material_offset,
            }   
            )
    return a
    

def read_index_data(rlg):
    filename = os.path.basename(rlg.name)
    print("Reading index data of: " +filename)
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )

    #find the section
    location = data.find(b'\x00\x01\xb0\x07')

    # get section size
    rlg.seek( location+4 ,0)
    section_size = int.from_bytes( rlg.read(4), "big" )
    start_of_data = rlg.tell()

    bytestr = b''

    bytestr = rlg.read(section_size)
    return bytestr


def read_index_data_group_by_mesh(rlg):
    mesh_data = read_mesh_data(rlg, True)
    index_data = read_index_data(rlg)
    vertex_attribute = read_vertex_attribute(rlg)
    # Create text file
    txt = open("output/_miscdata.txt", "w")
    # Loop 
    for m in range(0, len(mesh_data)):
        # Mesh data
        txt.write("================================ MESH " +str(m)+ ": ================================\n")
        for i in mesh_data[m]:
            txt.write( str(i) + " : " +str(mesh_data[m].get(i))+ "\n")
        # Vertex attributes of mesh
        txt.write("----------------------------------------------------------------\n")
        txt.write("VERTEX ATTRIBUTES: \n")
        mesh_vertex_attributes = vertex_attribute[10*m:10*(m+1)]
        for i in mesh_vertex_attributes:
            txt.write( str(i) + "\n")
        # Vertices of mesh
        txt.write("----------------------------------------------------------------\n")
        txt.write("VERTICES: \n")
        vertices = get_vertices_from_rlg(rlg, mesh_vertex_attributes)
        for i in vertices:
            # Number of the vertex inside the mesh
            vertex_number = hex( i["offset"]//12 - mesh_vertex_attributes[0]["offset"] )
            txt.write( "Offset: " +hex(i["offset"])+ " (Num: " +vertex_number+ ") Coordinates: " +str(i["values"])+ "\n")
        # Index data
        txt.write("----------------------------------------------------------------\n")
        txt.write("INDEX DATA: \n")
        index_data_end = mesh_data[m]['index_start_offset']+(mesh_data[m]['index_count']*2)
        for i in range(mesh_data[m]['index_start_offset'], index_data_end):
            txt.write( byte_hex( index_data[i]) )
            if(i%2 == 1):
                txt.write(" ")
            if(i%24 == 23):
                txt.write("\n")
        txt.write("\n\n\n\n\n\n")
    print("_miscdata.txt file successfully created in output folder")
    txt.close()



def create_obj(filename, vertices):
    # Remove .rlg from the filename
    filename = re.split(".rlg", filename)[0]
    # Create file
    obj = open("output/" +filename+ ".obj", "w")
    curr_group = -1
    for v in vertices:
        # Write the group of the vertices
        if(v["group"] != curr_group):
            curr_group = v["group"]
            line = "g group" + str( v["group"] ) + "\n"
            obj.write(line)
        # Write the vertex
        line = "v " + str( v["values"][0] ) + " " + str( v["values"][1] ) + " " + str( v["values"][2] ) + "\n"
        obj.write(line)
    print(filename + ".obj was successfully created in output folder")
    obj.close()


def create_obj_for_each_group(filename, vertices):
    # Remove .rlg from the filename
    filename = re.split(".rlg", filename)[0]
    curr_group = 0
    group_filename = filename + "_0"
    obj = open("output/" +group_filename+ ".obj", "w")

    for v in vertices:
        # Switch file
        if(v["group"] != curr_group):
            curr_group = v["group"]
            # Create file
            group_filename = filename + "_" + str(v["group"])
            obj.close()
            obj = open("output/" +group_filename+ ".obj", "w")
            line = "g group" + str( v["group"] ) + "\n"
            obj.write(line)
        # Write the vertex
        line = "v " + str( v["values"][0] ) + " " + str( v["values"][1] ) + " " + str( v["values"][2] ) + "\n"
        obj.write(line)
    print("files created in output folder")
    obj.close()


def read_obj(filename):
    print("filename: " +filename)
    obj = open("obj/" + filename + ".obj", "r")
    # find the file size
    obj.seek(0,2)
    file_size = obj.tell()
    # read the data
    obj.seek(0,0)
    data = obj.read( file_size )

    # read the vertices of the obj file and convert them to array
    array_of_vertices = []
    vertex = []
    num_str = ''
    ignore = False
    column = 0
    for i in data:
        # If first character of row is not v, ignore the whole row
        if(i != 'v' and column == 0):
            ignore = True
        # If current character is a comment ignore until new line
        if(i == '#'):
            ignore = True
        # If current character is part of a number, store it
        if(i in ['0','1','2','3','4','5','6','7','8','9','-','.','e']):
            num_str += i
        #  Increment the column
        column += 1
        # At the end of a number, parse the number
        if( (i == " " and len(num_str) != 0) or i == "\n"):
            if(not ignore):
                num = float(num_str)
                vertex.append(num)
            num_str = ''
            # Check if it's newline
            if(i == "\n"):
                if(len(vertex) > 0):
                    array_of_vertices.append(vertex)
                vertex = []
                ignore = False
                column = 0
        
    obj.close()
    return array_of_vertices


def generate_new_rlg(original_rlg):
    # Get the rlg filename without extension
    filename = os.path.basename(original_rlg.name)
    filename = re.split(".rlg", filename)[0]
    # Get the data from both the rlg and the obj
    try:
        new_vertices = read_obj(filename)
    except:
        print("Error: .obj file not found")
        return
    old_vertices = get_vertices_from_rlg(original_rlg, read_vertex_attribute(original_rlg))
    print("Found " + str(len(new_vertices)) + " Vertices in given obj file")
    print("Found " + str(len(old_vertices)) + " Vertices in given rlg file")
    if( len(new_vertices) != len(old_vertices)):
        print("Warning: The vertex count of the two files doesn't match. This may lead to errors, or the output rlg file might be incorrect")

    rlg = open("rlg/"+filename+".rlg", "rb")
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    # find the start of the section we need
    start_of_data = data.find(b'\x00\x01\xb0\x06')+8
    rlg.close()

    # Now it's time to copy the rlg file and replace its vertices 
    shutil.copyfile('./rlg/'+filename+'.rlg', './output/'+filename+'.rlg')
    rlg = open("output/"+filename+'.rlg', "r+b")
    vertex_num = 0

    for i in old_vertices:
        offset = i['offset']
        curr_location = start_of_data+offset
        rlg.seek(curr_location,0)
        for j in new_vertices[ vertex_num ]:
            j_hexstr = hex(struct.unpack('<I', struct.pack('<f', j))[0])
            if(j_hexstr != "0x0"):
                j_bytes = bytes.fromhex(j_hexstr[2:])
            else:
                j_bytes = b'\x00\x00\x00\x00'
            rlg.write( j_bytes )
        vertex_num += 1
    print(filename+".rlg file successfully created in output folder")
    



# Function to convert a bytearray into a clean string (so that it doesn't show ascii characters when printing, just hex)
def byte_hex_str(bytes):
    string = ""
    for i in bytes:
        string += byte_hex(i)
    return string

def byte_hex(byte):
        upper4 = (byte & 0xf0) >> 4 
        lower4 = byte & 0x0f
        chars = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
        return (chars[upper4] + chars[lower4])

def get_all_rlg_filenames():
    filenames_r = glob.glob("./rlg/*.rlg")
    filenames = []
    print("found", str(len(filenames_r)), "rlg files:")
    for i in filenames_r:
        file = re.split("\\\\", i)[1]
        print(file)
        filenames.append(file)
    return filenames

while True:
    r = input('''\n\n-- Select a command --
              
    COMMANDS FOR EXPORTING/IMPORTING FILES:
    e - Extract vertices from rlg file
    g - Generate new rlg (by starting from an original rlg and replacing its vertices with the ones of an obj)
              
    DEV STUFF:
    es - Extract vertices from rlg file and put them in separate OBJs (by group) (for dev purposes only. Those objs won't be useful to recreate an .rlg file)
    data - print misc data about each mesh of the .rlg file. Data will go into a txt file in the output folder
    va - print vertex attributes to txt file
    mesh - print mesh data to txt file
    index - print index data to txt file
    
    exit - Exit\n\n''')

    filenames = get_all_rlg_filenames()
    
    if(r == "e"):
        # Convert all the .rlg files to .obj
        for i in filenames:
            rlg = open("rlg/" + i, "rb")
            vertex_attributes = read_vertex_attribute(rlg)
            vertices = get_vertices_from_rlg(rlg, vertex_attributes)
            print("\n================================================================")
            create_obj(i, vertices)
            print("================================================================")
            rlg.close()
    elif(r == "g"):
        for i in filenames:
            rlg = open("rlg/" + i, "rb")
            print("\n================================================================")
            generate_new_rlg(rlg)
            print("================================================================")
            rlg.close()
    elif(r == "es"):
        # Convert all the .rlg files to .obj
        for i in filenames:
            rlg = open("rlg/" + i, "rb")
            vertex_attributes = read_vertex_attribute(rlg)
            vertices = get_vertices_from_rlg(rlg, vertex_attributes)
            print("\n================================================================")
            create_obj_for_each_group(i, vertices)
            print("================================================================")
            rlg.close()
    elif(r == "exit"):
        exit()
    elif(r == "va"):
        for i in filenames:
            rlg = open("rlg/" + i, "rb")
            print("\n================================================================")
            vertex_attribute = read_vertex_attribute(rlg)
            for a in vertex_attribute:
                print(a)
            rlg.close()
            # Print vertex attribute on text file
            txt = open("output/" +i+ "_vertexattribute.txt", "w")
            txt.write( str(len(vertex_attribute)) +" attributes found\n\n")
            for a in vertex_attribute:
                for j in a:
                    txt.write( j +" : "+ hex(a.get(j)) )
                    txt.write("\n")
                txt.write("------------------------------------------------\n")
            txt.close
            print("================================================================")
    elif(r == "mesh"):
        for i in filenames:
            rlg = open("rlg/" + i, "rb")
            print("\n================================================================")
            mesh_data = read_mesh_data(rlg, True)
            for m in mesh_data:
                print(m)
            rlg.close()
            # Print mesh data on text file
            txt = open("output/" +i+ "_meshdata.txt", "w")
            txt.write( str(len(mesh_data)) +" mesh data found\n\n")
            for m in mesh_data:
                for j in m:
                    txt.write( j +" : "+ hex(m.get(j)) )
                    txt.write("\n")
                txt.write("------------------------------------------------\n")
            txt.close
            print("================================================================")
    elif(r == "index"):
        for i in filenames:
            rlg = open("rlg/" + i, "rb")
            print("\n================================================================")
            bytestr = read_index_data(rlg)
            rlg.close()
            # Print index data on text file
            txt = open("output/" +i+ "_indexdata.txt", "w")
            string = byte_hex_str(bytestr)
            for j in range(0, len(string)):
                txt.write(string[j])
                if(j%12 == 11):
                    txt.write("\n")
            txt.close()
            print("Created txt file containing index data of " +i+ " in output folder")
            print("================================================================")
    elif(r == "data" or r == "d"):
        for i in filenames:
            rlg = open("rlg/" + i, "rb")
            read_index_data_group_by_mesh(rlg)
            rlg.close()
    else:
        print("invalid input")
    rlg.close()
    input("Press Enter to continue...")