from kivy.app import App
from kivy.deps import sdl2, glew
from kivy.uix.button import Button
from kivy.graphics import (Color,Rectangle,Line)
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.clock import Clock
from random import randint
from bisect import bisect_left
import json
import os
import gzip
DIALOG_FOLDER="dialog\\"
EXPORT_FOLDER="D:\Lessons\KIVY lesson\KIVY\KIVY\data"
DIGITS=8
DELTA=40

def random_number(N):
    start=10**(N-1)
    end=(10**N)-1
    return randint(start,end)




def getkey(node):
    if isinstance(node,dict):
        return node["number"]
    elif isinstance(node,Node):
        return node.number
    
def binary_search(array, target):
    lower = 0
    upper = len(array)
    i=0
    while lower < upper:  
        
        x = lower + (upper - lower) // 2
        val = array[x]
        if target == val:
            return x
        elif target > val:
            if lower == x:   
                break       
            lower = x
        elif target < val:
            upper = x

def sorted_insert(array,indicies,node):
     
     index=bisect_left(indicies,node.number)
     indicies.insert(index,node.number)
     array.insert(index,node)

class LinkLine(Line):
    def __init__(self,mother,father, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.mother=mother
       self.father=father
    def update(self):
        self.points=(self.mother.center_x,self.mother.center_y,self.father.center_x,self.father.center_y)


class Link(TextInput):
    def __init__(self,node,**kwargs):
      super().__init__(**kwargs)
      self.node=node
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.collide_point(touch.x,touch.y):
              if self.node.communication.tools.mode=="connecting":
                self.node.communication.tools.create_connection(mother=self)

class Name(Label):
    def __init__(self, node,**kwargs):
        super().__init__(**kwargs)
        self.node=node
    def on_touch_down(self, touch):
        super().on_touch_down(touch)

        if self.collide_point(touch.x,touch.y):

           self.node.communication.tools.create_connection(father=self.node)
           if self.node.communication.tools.alt_mode:
               self.node.to_branch()
    def on_touch_move(self, touch):
       super().on_touch_move(touch)
      
       if self.collide_point(touch.x,touch.y):
               self.node.center=(touch.x,touch.y)
               self.node.Main.center=self.node.center
               print(self.pos)
           
class Branch(FloatLayout):
    def __init__(self,communication, **kwargs):
     super().__init__(**kwargs)
     self.size_hint=(.2,.1)
     self.action=2
     self.number=random_number(8)

     self.nodes=[]
     self.nodes_data=[]
     self.communication=communication
     
     self.layout=BoxLayout(orientation="vertical")
     temp=BoxLayout()
     
     self.action_button=Button(text="Close",on_press=self.change)
     self.color=(1,0,1,1)
     temp.add_widget(self.action_button)
     self.active_button=Button(text="Active",on_press=self.become_active)
     temp.add_widget(self.active_button)

     self.layout.add_widget(Label(text=str(self.number),color =self.color))
     self.layout.add_widget(temp)
     
    
     
     self.add_widget(self.layout)
     self.layout.pos=self.pos
    def become_active(self,instance=None):
        self.communication.tools.active_branch=self
       
        
    def change(self,instance):
        if self.action==1:
            self.open()
            self.action=2
            self.action_button.text="Close"
        if self.action==2:
            self.close()
            self.action=1
            self.action_button.text="Open"

    def open(self):
        for node_data in self.nodes_data:
         
               self.communication.tools.load_node(node_data,branch = self )
        self.nodes_data=[]


    def close(self):
     for node in self.nodes:
        
        self.nodes_data.append(node.saving_for_project())
        self.communication.Main.remove_widget(node)
        self.nodes.remove(node)
        
       
    def on_touch_move(self, touch):
       super().on_touch_move(touch)
      
   
       if self.collide_point(touch.x,touch.y):
               self.center=(touch.x,touch.y)
               self.layout.center=self.center



class Node(FloatLayout):
    def __init__(self,Main,number="random",**kwargs):
        super().__init__(**kwargs)
        self.size_hint=(.2,.08)

      
        self.connected=False
        self.point=None
        self.branch=None
        self.temp=0
        self.Main=StackLayout(orientation='lr-tb')
        if number=="random":
           self.number=random_number(DIGITS)
        else:
            self.number=number
        self.name=Name(self,text="Node #"+str(self.number))
        self.communication=Main
        self.NPC_text=''
        self.answers_text=[]
        self.NPC_input=TextInput(text="NPC text")
        self.save_button=Button(text="Add answer",on_press=self.create_answer)
        self.delete_button=Button(text="Delete answer",on_press=self.delete_answer)
       
        self.Main.add_widget(self.name)
        self.Main.add_widget(self.NPC_input)
        self.Main.add_widget(self.save_button)
        self.Main.add_widget(self.delete_button)

        self.add_widget(self.Main)
        self.Main.pos=self.pos
        self.answers_labels=[]
        self.links=[]
        self.ans_link=[]
        
   
    def delete_answer(self,instance):
        try:
            deleted= self.ans_link.pop()
          
            self.Main.remove_widget(deleted)
            self.Main.remove_widget(deleted)
        except:
            print("Nothing to delete")

    def to_branch(self,given=None):

        if given==None:
            
            if self.communication.tools.active_branch==None:
                if self.branch!=None:
                  branch=self.branch
                else:
                    branch=None
            else:
                branch= self.communication.tools.active_branch
        else:
            branch=given
        if branch!=None:
            print("succes")
        
      
            self.communication.tools.active_branch.nodes.append(self)
            self.name.color=branch.color
            branch.nodes.append(self)
            self.branch=branch
         
        

        

    def create_answer(self,instance=None):
        temp=BoxLayout()
        answer=TextInput(text="Answer №"+str(len(self.answers_labels)+1),size_hint_x=2)
        answer.index=len(self.answers_labels)+1
        connection=Link(self,text="Link",background_color=[0, 1, 0, 1],multiline=False)
        connection.index=answer.index
        self.links.append(connection)
        self.ans_link.append(temp)

        temp.add_widget(answer)
        temp.add_widget(connection)
        self.answers_labels.append(answer)
     
        self.Main.add_widget(temp)
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
      

        if self.Main.collide_point(touch.x,touch.y):
            
           
            if self.communication.tools.mode=="deleting":                
                self.deleting()
            elif self.communication.tools.mode=="connecting":
                 self.communication.tools.create_connection()
        
                
        
   
        
     
   
      
    def move_up(self):
        self.pos=(self.pos[0],self.pos[1]+DELTA)
        self.Main.pos=self.pos
    
    def move_down(self):
        self.pos=(self.pos[0],self.pos[1]-DELTA)
        self.Main.pos=self.pos
      
    def move_right(self):
        self.pos=(self.pos[0]-DELTA,self.pos[1])
        self.Main.pos=self.pos
    
    def move_left(self):
        self.pos=(self.pos[0]+DELTA,self.pos[1])
        self.Main.pos=self.pos
       
    def saving_RAM(self):

        self.NPC_text=self.NPC_input.text
        self.answers_text=[]
        for label in self.answers_labels:
            self.answers_text.append(label.text)
    def minimize(self,mode=0):
        self.communication.Main.remove_widget(self)
      
       
        if mode==0:
          self.communication.active_nodes.remove(self)
       

        self.communication.minimized.append(self.saving_for_project())

        del self
     
   
    def is_active(self):
             if self.pos[0]<-200 or self.pos[0]>Window.width +200 or self.pos[1]<-200 or self.pos[1]> Window.height +200:
                return False
             else:
                return True
    def saving_for_project(self):
        self.saving_RAM()
        data={}
        i=0
        answers=[]
        for link in self.links:
          if len(link.text)<DIGITS:
                link.text=''
         
        for text in self.answers_text:
            answers.append([text,self.links[i].text])
            i+=1
        data["number"]=self.number
        data["NPC_text"]=self.NPC_input.text
        
        data["answers"]=answers
        data["pos"]=self.Main.pos
        return data
   
           
    def deleting(self):
        self.communication.Main.remove_widget(self)
       # self.communication.active_nodes.remove(self)
        self.communication.all.remove(self)
        self.communication.node_indecies.remove(self.number)


class Tools(BoxLayout):
    def __init__(self,Main, **kwargs):
        super().__init__(**kwargs)
        self.communication=Main
        self.conn_in=None
        self.conn_out=None
        self.mode="editing"
        self.alt_mode=False
        self.moving=None
        self.mode_counter=0
        self.project_file=''
        self.modes=["editing","deleting","connecting"]
        self.lines=[]
        self.active_branch=None
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self, 'text')
        
        
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
    def update_drawing(self,deleted_connection=None):
           self.canvas.clear()
           duration_of_function(self.connect_all)
          
    def keyboard_closed(self):
     
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard = None

    def restore_keyboard(self):
         self.keyboard = Window.request_keyboard(self.keyboard_closed, self, 'text')
         self.keyboard.bind(on_key_down=self.on_keyboard_down)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
       
            self.shortucts(keycode,text,modifiers)
    
    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        self.moving=None
     
    def shortucts(self,keycode, text, modifiers):
         if modifiers==["ctrl"]:
                if text=="s":
                    self.save_project()
                elif text=="e":
                    self.export()
                #elif text=="b":
                  
                #    new=Branch(self.communication,center_x=Window.mouse_pos[0],center_y=Window.mouse_pos[1])

                #    self.communication.branches.append(new)
                #    self.communication.Main.add_widget(new)
                    

         if text=="b":
            self.alt_mode= not self.alt_mode
           
         if modifiers==["ctrl"] :
                if text=="a":
                    self.createNode(Window.mouse_pos[0],Window.mouse_pos[1])
            
               
         if keycode[1]=="shift"or keycode[1]=="rshift":
              self.switch_mode()
         
         self.move(keycode[1])
        
       
    def createNode(self,x,y):
      
        node=Node(self.communication,pos=(x,y),size=(100,100))

        self.communication.active_nodes.append(node)
       
        sorted_insert(self.communication.all,self.communication.node_indecies,node)

        
        self.communication.Main.add_widget(node)
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        for line in self.lines:
            line.update()
       
        
        
    def update_lines(self):
         for line in self.lines:
            line.update()
    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        self.update_lines()
        if self.mode!="editing":

               self.restore_keyboard()
            
   
    def create_connection(self,father=None,mother=None):
        """
        mother = Link
        father = Node
        """
        if mother!=None:
                
                
                              self.conn_in=mother
                              mother.node.connected=True
                              mother.node.temp=1
                              mother.node.point=(mother.center_x,mother.center_y)
                              
                             
        elif  father!=None and self.conn_in!=None:
              
                  
                         self.conn_in.text=str(father.number)
                         
                         father.connected=True
                         father.point=(father.center_x,father.center_y)
                         father.temp=2
                         with self.canvas:
                               Color(0,1,0)
                               self.lines.append(LinkLine(mother=self.conn_in,father=father,points=((self.conn_in.center_x, self.conn_in.center_y),father.point)))
                         self.conn_in=None   
                         self.conn_out=None
                        
    def switch_mode(self,instance=None):
        self.mode_counter+=1
        self.mode_counter=self.mode_counter%len(self.modes)
        self.mode=self.modes[self.mode_counter]
        self.instance.text=self.mode
 
    def update_nodes(self,dt=None):
        for node in self.communication.active_nodes:
               if not node.is_active():
                    node.minimize()     
                   
           
                
           

        for node_data in self.communication.minimized:
           
            if node_data["pos"][0] >-200 and node_data["pos"][1]<Window.width+200:
               
                if node_data["pos"][1]>-200 and node_data["pos"][1] <Window.height+200:
                  
                    self.restore_node(node_data)
                    
                    
    def load_node(self,node_data,branch=None,mode=0):
           node=Node(self.communication,pos=(node_data["pos"][0],node_data["pos"][1]),number=node_data["number"])
           node.Main.pos=node.pos
           node.NPC_input.text=node_data["NPC_text"]
           i=0
           node.to_branch(branch)
           while i<len(node_data['answers']):
               node.create_answer()
               i+=1
           i=0
           for answer in node.answers_labels:
               answer.text=node_data['answers'][i][0]
               i+=1
           i=0
           for link in node.links:
               link.text=node_data['answers'][i][1]
               i+=1
           if mode==0:
             sorted_insert(self.communication.all,self.communication.node_indecies,node)
           if node.is_active():
              self.communication.active_nodes.append(node)
           else:
               node.minimize(1)
           self.communication.Main.add_widget(node)
         
          
           
           return node
    def restore_node(self,node_data):
        
   
        node=self.load_node(node_data,mode = 1)
        self.connect_node(node)

        self.communication.minimized.remove(node_data)
       
        
        
       
       
    def move(self,num):
        if num=="right":
           for node in self.communication.active_nodes:
            node.move_right()
          
           for node in self.communication.minimized:
            node["pos"][0]-=DELTA
            

       
        elif num=="left":
           for node in self.communication.active_nodes:
            node.move_left()
           for node in self.communication.minimized:
            node["pos"][0]+=DELTA
        elif num=="down":
           for node in self.communication.active_nodes:
            node.move_up()
           for node in self.communication.minimized:
            node["pos"][1]+=DELTA
       
           

        elif num =="up":
           for node in self.communication.active_nodes:
            node.move_down()
           for node in self.communication.minimized:
            node["pos"][1]-=DELTA

      #  self.update_nodes()

        
        self.update_lines()
        
   

       

   
    
    def save_project(self,instance=None,foldername="projects"):
        data=[]
        
        if self.project_file=='':
            self.project_file=input("ENTER PROJECT NAME : ")+".json"

        for node in self.communication.all:
            data.append(node.saving_for_project())
       
        
        with open(foldername+"\\"+self.project_file,'w') as file:
            json.dump(data,file)


       


        if input("wanna export? to "+EXPORT_FOLDER+" (y/n) : ").lower()=="y":
            

            with gzip.GzipFile(EXPORT_FOLDER+"\\data.gz",'w') as fid_gz:
    
         
        
                
                json_str = json.dumps(data)
                json_str=json_str.encode()
           
                fid_gz.write(json_str)
        
        print("All "+str(len(self.communication.all))+"nodes" +"were saved into json file, for connecting them to game read docs")

    def load_project(self,instance=None):
        for node in self.communication.all:
            self.communication.Main.remove_widget(node)

        if len(self.communication.all)>0:
            a=input("Save current project y/n")
            if a=='1' or a=='y':
               self.save_project()
        self.communication.all=[]
        self.communication.node_indecies=[]
        self.communication.active_nodes=[]
        filename=self.choosing_project()
        print(filename)
        with open(filename) as file:
            data=json.load(file)
      
        data=sorted(data,key=getkey)
        for node_data in data:
           
           self.load_node(node_data)

        self.connect_all()
       
        self.update_lines()
    def choosing_project(self):
        while True:
         files_r=[]
         for root,dirs,files in os.walk('projects'):
             for filename in files:
                 if filename.endswith(".json"):
                     print(filename)
                     files_r.append(filename)
         a=input("enter full filename of project :")
         if a in files_r:
                filename=a
                break
        
        
         
       
        
        return "projects\\"+filename
  
    def connect(self,father,mother):
       
        father.connected=True
        father.point=(father.center_x,father.center_y)
        father.temp=2
        father.connected=True
        mother.parent.parent.temp=1
        mother.parent.parent.point=(mother.center_x,mother.center_y)
        with self.canvas:
            Color(0,1,0)
            self.lines.append(LinkLine(mother=mother,father=father,points=((mother.center_x, mother.center_y),father.point)))
       
   
                           
    def connect_node(self,main):
        for link in main.links:
                if  link.text!='':
                       try:
                           link_int=int(link.text)
                       except ValueError:
                           link_int=0
                       index=binary_search(self.communication.node_indecies,link_int)
                       if index!=None:
                           node=self.communication.all[index]
                           self.connect(node,link)
    def connect_all(self):
        self.canvas.clear()
        self.lines=[]

       
       
        for node in self.communication.all:
            self.connect_node(node)
            
                           
                        
                   
        
        
                

 
             


                   
                      

def duration_of_function(function):
        import time
        import json
        start=time.time()
        def print_elapsed():
            print("-----"+str(time.time()-start)+"-----")

        function()
       
        print_elapsed()
 

class DialogCreatorApp(App):
    def build(self):
        self.mode="editing"
        self.Main=FloatLayout()
        self.all=[]
        
        self.tools=Tools(self)

        self.Main.add_widget(self.tools)
        temp=Button(text=self.tools.mode, pos_hint={'x':.90, 'y':.9},size_hint=(.1, .1),on_press=self.tools.switch_mode)
        self.tools.instance=temp

        self.Main.add_widget(temp)
       
        self.Main.add_widget(Button(text="Save project",pos_hint={'x':0,'y':.9},size_hint=(.1,.1),on_press=self.tools.save_project))
        self.Main.add_widget(Button(text="Connect all",pos_hint={'x':.1,'y':0},size_hint=(.1,.1),on_press=self.tools.update_drawing))
        self.Main.add_widget(Button(text="Load project",pos_hint={'x':.9,'y':0},size_hint=(.1,.1),on_press=self.tools.load_project))
        
        self.node_indecies=[]
        self.active_nodes=[]
        self.minimized=[]
        self.branches=[]
        return self.Main
   

  
       
       
       
   
 
        
        
DialogCreatorApp().run()