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
    a = []
    while rlg.tell() < start_of_data+section_size:
        current_byte = rlg.tell() - start_of_data
        stride = 4
        # check vertex attribute offset
        for i in vertex_attributes:
            if( i['offset'] <= current_byte ):
                stride = i['stride']

        new_vector = []
        for i in range(0, stride//4):
            bytes = rlg.read(4)
            f = struct.unpack( '!f', bytes )[0]
            new_vector.append(f)
        a.append( {
            "offset" : current_byte,
            "values" : new_vector
        } )
    for i in range(0, len(a)):
        print(a[i])
    rlg.close()

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


def byte_hex_str(bytes):
    string = ""
    for i in bytes:
        upper4 = (i & 0xf0) >> 4 
        lower4 = i & 0x0f
        chars = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
        string += (chars[upper4] + chars[lower4])
    return string



vertex_attributes = read_vertex_attribute()
read_vertex_data(vertex_attributes)