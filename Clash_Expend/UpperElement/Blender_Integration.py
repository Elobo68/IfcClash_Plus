import bpy


def Test():
   LesObjets=bpy.data.objects
   print("esObjets",LesObjets)



if __name__ == "__main__":
   print("Hello World: run from Blender Text Editor")
   
   
else:
   print("Hello World: run from VSCode")
   print(f"NOTE. __name__ is : {__name__}")

Test()


