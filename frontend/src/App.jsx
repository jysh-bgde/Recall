import { useContext, useEffect, useState } from 'react'

import './App.css'
import { useNavigate } from 'react-router-dom'

function App() {
  const [file, setFile] = useState();
  
  const navigate = useNavigate()
  const [isUploadingFile, setIsUploadingFile] = useState(false)
  function handleChange(event)
  {
   if(event.target.files)
   {

     setFile(event.target.files[0])
   
   }   
  }

  async function handleSubmit(e)
  {
     e.preventDefault();
     if (!file || isUploadingFile) return;
    setIsUploadingFile(true)
    const formData = new FormData()
    formData.append("file", file)

    const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
        })

    const data = await response.json()
    
      setIsUploadingFile(false)
    navigate('/chat', {state: {filename : file.name}})

  }

  useEffect(()=>{
    console.log(file)
  }, [file])

  return (
   
    <div className='mainDiv'>

    <div className='formDiv'>

   <form onSubmit={handleSubmit}>
    <label htmlFor="file"/>
    <input className="inputFile" type="file" name="file" id="file" placeholder='upload file' onChange={handleChange} accept='application/pdf' />
    <button type='submit' className='fileSubmitButton' disabled ={ !file || isUploadingFile }> {isUploadingFile ? "Uploading..." : "Submit"}</button>
   </form>
    </div>
    </div>
  
  )
}

export default App
