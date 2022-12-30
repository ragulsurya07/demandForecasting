import React from 'react'
import { useState } from 'react'
import axios from 'axios'
import Plot from "react-plotly.js";
import pic from '../Screenshot from 2022-12-22 18-07-09.png'


function Uploadfile() {
  const [result,setResult] = useState([])
  const [month, setMonth] = useState([]);
  
  let uploadInput;
  const handleUpload = async(e) =>{
    e.preventDefault()
    const data = new FormData();
    data.append('file', uploadInput.files[0])

    try {
      const res = await axios.post('/upload',data)
      setResult(res.data);
      console.log('res.data', res.data);
    } catch(error) {
      console.log(error);
    }


    const monthArr = [
      'January',
      'Feburary',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December'
    ]

    setMonth((monthArr));

  }

  return (
    <form onSubmit={(e)=>{handleUpload(e)}}>
      <div className='CSV'>
        <p> (or) </p>
        <input ref={(e) => {uploadInput = e}}  type="file" />
        <button data-bs-toggle="modal" data-bs-target="#CSVfileUpload" value="submit">Upload</button>
        <h5><span>Note : </span>Check your file format before uploading file, because this only accept .CSV file only.</h5>
        <h3>The file's structure must be in 2-coloumns first one is month & second one is sales. (or) If you have any doubt see the below figure.</h3>
        <img alt='screenshot' src={pic}></img>
      </div>

      <div className="modal" id="CSVfileUpload">
        <div className="modal-dialog modal-dialog-centered modal-lg">
          <div className="modal-content">
            <div className="modal-header">
              <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div className="modal-body">
            {result.data && result.data.map((map,i)=>(
              <div><p key={i}> {month[i]} - { Math.round(map) }</p></div>
            ))}
            <div className='graph'>
            <Plot
              data={[
                {
                    x: [1,2,3,4,5,6,7,8,9,10,11,12],
                    y: result.data,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Best fit Line',
                    marker: {color: 'red'},
                }, {
                  x: [1,2,3,4,5,6,7,8,9,10,11,12],
                  y: result.yvalues,
                  type: 'scatter',
                  mode: 'markers',
                  name: 'Actual Sales',
                  marker: {color: 'green'},
                }]}
                layout={ {width: 720, height: 440, title: 'Sales Comparison', font: {family: 'Courier New, monospace',size: 15,color: '#2E2E2E'}} }
            />
            </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </form>
  );
}

export default Uploadfile;