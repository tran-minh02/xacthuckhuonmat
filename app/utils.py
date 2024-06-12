import face_recognition as fr
import numpy as np
from profiles.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import logout
from PIL import Image
from django.core.files.base import ContentFile
import io
def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'

# Truy cứu ảnh người dùng thông qua username
def get_encoded_faces(username):
    
    user = User.objects.get(username = username)
    qs = Profile.objects.get(user = user)

    photo = qs.photo.path 
    print(photo)
    encoding = None

    face = fr.load_image_file(photo)

    face_encodings = fr.face_encodings(face)[0]
    return face_encodings

# Xác thực ảnh giữa tren ảnh đầu vào và ảnh được lưu  
def classify_face(img, username):
    # Lấy ảnh khuôn mặt thông qua username
    faces = get_encoded_faces(username)
    print(img)
    # Đưa input khuôn mặt vào
    img = fr.load_image_file(img)
 
    try:
        # Tìm vị trí các khuôn mặt trong ảnh đầu vào 
        face_locations = fr.face_locations(img)
        if(len(face_locations) == 0) :
            print('No face found')
            return [False]
        # Mã hóa hình các khuôn mặt
        unknown_face_encodings = fr.face_encodings(img, face_locations)[0]
        matches = fr.compare_faces([faces],unknown_face_encodings)
        return matches
    except:
        return False
    
def save_face(img,user):
    '''
    Nhân vào một hình ảnh trả về khuôn mặt có trong ảnh , nếu không có trả về 0 , có trả về một ảnh 
    '''
    img = np.array(img)
    try:
        # Tìm vị trí cảu các khuôn mặt trong ảnh 
        face_locations = fr.face_locations(img)
        if(len(face_locations) == 0) :
            print('No face found')
            user.delete()
            return False
        for i, face_location in enumerate(face_locations):
            top, right, bottom, left = face_location
    
        # Cắt khuôn mặt từ hình ảnh gốc
        face_image = img[top:bottom, left:right]

        # Tạo đối tượng Image từ mảng NumPy của khuôn mặt
        pil_image = Image.fromarray(face_image)
        cropped_image_io = io.BytesIO()
        pil_image.save(cropped_image_io,format='PNG')
        cropped_image_file = ContentFile(cropped_image_io.getvalue())
        x = Profile.objects.get(user=user)
        x.photo.save('upload.png',cropped_image_file)
        x.save()
        print(x.photo.path)
        return True
    except:
        user.delete()
        return False