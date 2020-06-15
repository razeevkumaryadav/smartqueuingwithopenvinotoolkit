#!/usr/bin/env python
# coding: utf-8

# # Step1: Create the Python Script
# 
# In the cell below, you will need to complete the Python script and run the cell to generate the file using the magic `%%writefile` command. Your main task is to complete the following methods for the `PersonDetect` class:
# * `load_model`
# * `predict`
# * `draw_outputs`
# * `preprocess_outputs`
# * `preprocess_inputs`
# 
# For your reference, here are all the arguments used for the argument parser in the command line:
# * `--model`:  The file path of the pre-trained IR model, which has been pre-processed using the model optimizer. There is automated support built in this argument to support both FP32 and FP16 models targeting different hardware.
# * `--device`: The type of hardware you want to load the model on (CPU, GPU, MYRIAD, HETERO:FPGA,CPU)
# * `--video`: The file path of the input video.
# * `--output_path`: The location where the output stats and video file with inference needs to be stored (results/[device]).
# * `--max_people`: The max number of people in queue before directing a person to another queue.
# * `--threshold`: The probability threshold value for the person detection. Optional arg; default value is 0.60.

# In[6]:


get_ipython().run_cell_magic('writefile', 'person_detect.py', '\nimport numpy as np\nimport time\nfrom openvino.inference_engine import IENetwork, IECore\nimport os\nimport cv2\nimport argparse\nimport sys\n\n\nclass Queue:\n    \'\'\'\n    Class for dealing with queues\n    \'\'\'\n    def __init__(self):\n        self.queues=[]\n\n    def add_queue(self, points):\n        self.queues.append(points)\n\n    def get_queues(self, image):\n        for q in self.queues:\n            x_min, y_min, x_max, y_max=q\n            frame=image[y_min:y_max, x_min:x_max]\n            yield frame\n    \n#     def check_coords(self, coords,w,h):\n#         d={k+1:0 for k in range(len(self.queues))}\n#         for coord in coords:\n#             for i, q in enumerate(self.queues):\n#                 if coord[0]>q[0] and coord[2]<q[2]:\n#                     d[i+1]+=1\n#         return d\n     def check_coords(self, coords, initial_w, initial_h):\n        \'\'\'\n        Function have been modified.\n        \'\'\'\n        d={k+1:0 for k in range(len(self.queues))}\n        \n        dummy = [\'0\', \'1\' , \'2\', \'3\']\n        \n        for coord in coords:\n            xmin = int(coord[3] * initial_w)\n            ymin = int(coord[4] * initial_h)\n            xmax = int(coord[5] * initial_w)\n            ymax = int(coord[6] * initial_h)\n            \n            dummy[0] = xmin\n            dummy[1] = ymin\n            dummy[2] = xmax\n            dummy[3] = ymax\n            \n            for i, q in enumerate(self.queues):\n                if dummy[0]>q[0] and dummy[2]<q[2]:\n                    d[i+1]+=1\n        return d\n    \n\n\nclass PersonDetect:\n    \'\'\'\n    Class for the Person Detection Model.\n    \'\'\'\n\n    def __init__(self, model_name, device, threshold=0.60):\n        self.model_weights=model_name+\'.bin\'\n        self.model_structure=model_name+\'.xml\'\n        self.device=device\n        self.threshold=threshold\n\n        try:\n            self.model=IENetwork(self.model_structure, self.model_weights)\n        except Exception as e:\n            raise ValueError("Could not Initialise the network. Have you enterred the correct model path?")\n\n        self.input_name=next(iter(self.model.inputs))\n        self.input_shape=self.model.inputs[self.input_name].shape\n        self.output_name=next(iter(self.model.outputs))\n        self.output_shape=self.model.outputs[self.output_name].shape\n\n    def load_model(self):\n    \'\'\'\n    TODO: This method needs to be completed by you\n    \'\'\'\n    self.core = IECore()\n    try:\n        self.net = self.core.network_load(network=self.model, device_name = self.device, num_requests = 1)\n    except Exception as e:\n        raise ValueError("could not load the network")\n        \n    def predict(self, image):\n    \'\'\'\n    TODO: This method needs to be completed by you\n    \'\'\'\n    input_name = self.input_name\n    input_img = self.preprocess_input(image)\n    \n#     inference\n    input_dict = {input_name:input_img}\n    #ansync request for specified request\n    infer_request = self.net.start_async(request_id=1, input=input_dict)\n    infer_status = infer_request.await()\n    \n    try:\n        if infer_status = 0:\n            output = infer_request.outputs[self.output_name]\n        \n        return output,image\n    \n    except Exception as e:\n    \n        raise ValueError("eror in predicting ")\n    \n    def draw_outputs(self, coords, frame, initial_w, initial_h):\n    \'\'\'\n    TODO: This method needs to be completed by you\n    \'\'\'\n    current_count = 0\n    det =[]\n    \n    try:\n    \n        for obj in coords[0][0]:\n         # Draw bounding box for the detected object when it\'s probability is greater than the specified threshold\n            if obj[2] > self.threshold:\n                xmin = int(obj[3] * initial_w)\n                ymin = int(obj[4] * initial_h)\n                xmax = int(obj[5] * initial_w)\n                ymax = int(obj[6] * initial_h)\n                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 55, 255), 1)\n                current_count = current_count + 1\n                \n                det.append(obj)\n                \n        return frame, current_count, det\n    \n    except Exception as e:\n                \n        raise ValueError("Error in drawing bounding box")\n\n        \n    def preprocess_outputs(self, outputs):\n    \'\'\'\n    TODO: This method needs to be completed by you\n    \n    \'\'\'\n    output_dict = {}\n        for output in outputs:\n            output_name = self.output_name\n            output_img = output\n            output_dict[output_name] = output_img\n        \n        return output_dict\n    \n        return output\n    \n    \n#         raise NotImplementedError\n\n    def preprocess_input(self, image):\n    \'\'\'\n    TODO: This method needs to be completed by you\n    \'\'\'\n    input_img = image\n        \n        # Preprocessing input\n       \n        n, c, h, w = self.input_shape\n        \n        input_img=cv2.resize(input_img, (w, h), interpolation = cv2.INTER_AREA)\n        \n        # Change image from HWC to CHW\n        input_img = input_img.transpose((2, 0, 1))\n        input_img = input_img.reshape((n, c, h, w))\n    return input_img\n#         raise NotImplementedError\n\n\ndef main(args):\n    model=args.model\n    device=args.device\n    video_file=args.video\n    max_people=args.max_people\n    threshold=args.threshold\n    output_path=args.output_path\n\n    start_model_load_time=time.time()\n    pd= PersonDetect(model, device, threshold)\n    pd.load_model()\n    total_model_load_time = time.time() - start_model_load_time\n\n    queue=Queue()\n    \n    try:\n        queue_param=np.load(args.queue_param)\n        for q in queue_param:\n            queue.add_queue(q)\n    except:\n        print("error loading queue param file")\n\n    try:\n        cap=cv2.VideoCapture(video_file)\n    except FileNotFoundError:\n        print("Cannot locate video file: "+ video_file)\n    except Exception as e:\n        print("Something else went wrong with the video file: ", e)\n    \n    initial_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))\n    initial_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))\n    video_len = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))\n    fps = int(cap.get(cv2.CAP_PROP_FPS))\n    out_video = cv2.VideoWriter(os.path.join(output_path, \'output_video.mp4\'), cv2.VideoWriter_fourcc(*\'avc1\'), fps, (initial_w, initial_h), True)\n    \n    counter=0\n    start_inference_time=time.time()\n\n    try:\n        while cap.isOpened():\n            ret, frame=cap.read()\n            if not ret:\n                break\n            counter+=1\n            \n            coords, image= pd.predict(frame)\n            num_people= queue.check_coords(coords)\n            print(f"Total People in frame = {len(coords)}")\n            print(f"Number of people in queue = {num_people}")\n            out_text=""\n            y_pixel=25\n            \n            for k, v in num_people.items():\n                out_text += f"No. of People in Queue {k} is {v} "\n                if v >= int(max_people):\n                    out_text += f" Queue full; Please move to next Queue "\n                cv2.putText(image, out_text, (15, y_pixel), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)\n                out_text=""\n                y_pixel+=40\n            out_video.write(image)\n            \n        total_time=time.time()-start_inference_time\n        total_inference_time=round(total_time, 1)\n        fps=counter/total_inference_time\n\n        with open(os.path.join(output_path, \'stats.txt\'), \'w\') as f:\n            f.write(str(total_inference_time)+\'\\n\')\n            f.write(str(fps)+\'\\n\')\n            f.write(str(total_model_load_time)+\'\\n\')\n\n        cap.release()\n        cv2.destroyAllWindows()\n    except Exception as e:\n        print("Could not run Inference: ", e)\n\nif __name__==\'__main__\':\n    parser=argparse.ArgumentParser()\n    parser.add_argument(\'--model\', required=True)\n    parser.add_argument(\'--device\', default=\'CPU\')\n    parser.add_argument(\'--video\', default=None)\n    parser.add_argument(\'--queue_param\', default=None)\n    parser.add_argument(\'--output_path\', default=\'/results\')\n    parser.add_argument(\'--max_people\', default=2)\n    parser.add_argument(\'--threshold\', default=0.60)\n    \n    args=parser.parse_args()\n\n    main(args)')


# # Next Step
# 
# Now that you've run the above cell and created your Python script, you will create your job submission shell script in the next workspace.
# 
# **Note**: As a reminder, if you need to make any changes to the Python script, you can come back to this workspace to edit and run the above cell to overwrite the file with your changes.
