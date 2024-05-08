import os, struct, math

def read_vertex_floats():
    # TODO: detect file name automatically
    rlg = open("rlg/mario.rlg", "rb")
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    #print( byte_hex_str(data) )

    #find the section
    location = data.find(b'\xb0\x06')
    print( hex(location) )

    floats = []
    rlg.seek( location+6 ,0)
    while rlg.tell() < file_size:
        bytes = rlg.read(4)
        f = struct.unpack( '!f', bytes )[0]
        if( math.isnan(f) or math.isinf(f) ):
            break
        floats.append(f)
    print(floats[:10])
    rlg.close()

def read_vertex_data(vertex_attributes):
    # TODO: detect file name automatically
    rlg = open("rlg/mario.rlg", "rb")
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    #print( byte_hex_str(data) )

    #find the section
    location = data.find(b'\xb0\x06')
    print( hex(location) )

    start_of_data = location+6
    rlg.seek( location+2 ,0)
    section_size = int.from_bytes( rlg.read(4), "big" )
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

        if(last_0x4 == '0xb0' and unknown_0x4 == '0x67'):
            group += 1
        last_0x4 = unknown_0x4

        new_vector = []
        for i in range(0, stride//4):
            bytes = rlg.read(4)
            f = struct.unpack( '!f', bytes )[0]
            new_vector.append(f)
        a.append( {
            "offset" : current_byte,
            "type" : unknown_0x4, # TODO: try to extract only vectors with this value as 0x67 or as 0xfe, they might be vertices (or normals)
            "group" : group,
            "values" : new_vector
        } )
    
    # fliter only the vertices we need
    vertices = []

    for i in a:
        if( i['type'] == '0x67' ):
            vertices.append( i )
    rlg.close()
    return vertices


def read_vertex_attribute():
    # TODO: detect file name automatically
    rlg = open("rlg/mario.rlg", "rb")
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    #print( byte_hex_str(data) )

    #find the section
    location = data.find(b'\xb0\x05')
    print( hex(location) )

    # read data
    rlg.seek( location+2 ,0)
    section_size_b = rlg.read(4)
    section_size = int.from_bytes( section_size_b, "big" )
    a = []
    while rlg.tell() < location+6+section_size:
        offset = int.from_bytes( rlg.read(4), "big" )
        unknown_0x4 = int.from_bytes( rlg.read(1), "big" )
        stride = int.from_bytes( rlg.read(1), "big" )
        rlg.read(2)

        a.append( {
            "offset" : offset,
            "0x4" : hex(unknown_0x4), # 67 fe cc ed 52 c0 d6 d7 d4 b0
            "stride" : stride
        } )
    for v in a:
        print(v)
    rlg.close()
    return a


def read_mesh_data():
    # TODO: detect file name automatically
    rlg = open("rlg/mario.rlg", "rb")
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    #print( byte_hex_str(data) )

    #find the section
    location = data.find(b'\xb0\x04')
    print( hex(location) )

    # read data
    rlg.seek( location+2 ,0)
    section_size_b = rlg.read(4)
    section_size = int.from_bytes( section_size_b, "big" )
    a = []
    while rlg.tell() < location+6+section_size:
        index_start_offset = int.from_bytes( rlg.read(4), "big" )
        index_flags = int.from_bytes( rlg.read(4), "big" )
        face_type = int.from_bytes( rlg.read(1), "big" )
        attribute_count = int.from_bytes( rlg.read(1), "big" )
        rlg.read(4)
        material_hash_id = int.from_bytes( rlg.read(4), "big" )
        mesh_hash_id = int.from_bytes( rlg.read(4), "big" )
        rlg.read(8)
        material_offset = int.from_bytes( rlg.read(4), "big" )
        rlg.read(14)

        a.append( { 
            "index_start_offset" : index_start_offset,
            "index_flags" : index_flags,
            "face_type" : face_type,
            "attribute_count" : attribute_count,
            "material_hash_id" : material_hash_id,
            "mesh_hash_id" : mesh_hash_id,
            "material_offset" : material_offset,
        }   
        )
    for m in a:
        print(m)
    rlg.close()


def create_obj(vertices):
    obj = open("output/file.obj", "w")
    for v in vertices:
        line = "v " + str( v["values"][0] ) + " " + str( v["values"][1] ) + " " + str( v["values"][2] ) + "\n"
        obj.write(line)
    obj.close()


def read_obj():
    obj = open("obj/file.obj", "r")
    # find the file size
    obj.seek(0,2)
    file_size = obj.tell()
    # read the data
    obj.seek(0,0)
    data = obj.read( file_size )
    # read the vertices of the obj file and convert them to array
    a = []
    vertex = []
    num_str = ''
    for i in data:
        if(i in ['0','1','2','3','4','5','6','7','8','9','-','.','e']):
            num_str += i
        if( (i == " " and len(num_str) != 0) or i == "\n"):
            num = float(num_str)
            vertex.append(num)
            num_str = ''
            if(i == "\n"):
                a.append(vertex)
                vertex = []

    obj.close()
    return a


def edit_rlg():
    new_vertices = read_obj()
    old_vertices = read_vertex_data(read_vertex_attribute())
    print(len(new_vertices))
    print(len(old_vertices))

    rlg = open("rlg/mario.rlg", "rb")
    # find the file size
    rlg.seek(0,2)
    file_size = rlg.tell()
    # read the data
    rlg.seek(0,0)
    data = rlg.read( file_size )
    # find the start of the section we need
    start_of_data = data.find(b'\xb0\x06')+6
    rlg.close()

    # Now it's time to write on the file
    rlg = open("rlg/mario.rlg", "r+b")
    vertex_num = 0

    for i in old_vertices:
        offset = i['offset']
        curr_location = start_of_data+offset
        rlg.seek(curr_location,0)
        for j in new_vertices[ vertex_num ]:
            j_hexstr = hex(struct.unpack('<I', struct.pack('<f', j))[0])
            print( j_hexstr )
            if(j_hexstr != "0x0"):
                j_bytes = bytes.fromhex(j_hexstr[2:])
            else:
                j_bytes = b'\x00\x00\x00\x00'
            rlg.write( j_bytes )
        vertex_num += 1




def byte_hex_str(bytes):
    string = ""
    for i in bytes:
        upper4 = (i & 0xf0) >> 4 
        lower4 = i & 0x0f
        chars = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
        string += (chars[upper4] + chars[lower4])
    return string


while True:
    r = input("What do you want to do?\n\n1)rlg -> obj\n2)obj -> rlg\n")

    if(r == "1"):
        vertex_attributes = read_vertex_attribute()
        vertices = read_vertex_data(vertex_attributes)
        create_obj(vertices)
    elif(r == "2"):
        edit_rlg()
    else:
        print("invalid input")