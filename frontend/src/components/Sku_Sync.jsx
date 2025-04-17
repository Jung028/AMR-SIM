import React, { useState, useEffect } from 'react';
import Editor from 'react-simple-code-editor';
import "../styles/Sku_Sync.css";

const defaultJson = `{
  "header": {
    "warehouse_code": "geekplus",
    "user_id": "testUser",
    "user_key": "111111"
  },
  "body": {
    "sku_amount": 1,
    "sku_list": [
      {
        "owner_code": "lidong",
        "sku_id": "ERPSKU001",
        "sku_code": "sku001",
        "sku_name": "memory",
        "sku_price": 18.9,
        "unit": "EACH",
        "remark": "128GB",
        "dimensions": {
          "sku_length": 15.5,
          "sku_width": 20,
          "sku_height": 8.5,
          "sku_volume": 100.25
        },
        "weight": {
          "sku_net_weight": 200,
          "sku_gross_weight": 230
        },
        "stock_limits": {
          "sku_min_count": 100,
          "sku_max_count": 20000
        },
        "sku_shelf_life": 90,
        "sku_specification": "2piece/box",
        "sku_status": 1,
        "sku_abc": "30",
        "is_sequence_sku": 0,
        "sku_production_location": "Beijing",
        "sku_brand": "AMD",
        "sku_attributes": {
          "sku_size": "XL",
          "sku_color": "red",
          "sku_style": "show"
        },
        "sku_pic_url": "http://tianmao.com/h/sku001.jpg",
        "is_bar_code_full_update": 1,
        "sku_bar_code_list": [
          {
            "sku_bar_code": "code1",
            "input_date": 1102098121000
          }
        ],
        "sku_packing": [
          {
            "sku_packing_spec": "1*10*6",
            "primary": {
              "sku_packing_code": "code1",
              "sku_packing_length": 10,
              "sku_packing_width": 10,
              "sku_packing_height": 10,
              "sku_packing_volume": 1000,
              "sku_packing_weight": 50,
              "sku_packing_amount": 1
            },
            "secondary": {
              "sku_packing_code": "PM0002",
              "sku_packing_length": 30,
              "sku_packing_width": 30,
              "sku_packing_height": 30,
              "sku_packing_volume": 27000,
              "sku_packing_weight": 300,
              "sku_packing_amount": 6
            },
            "tertiary": {
              "sku_packing_code": "PL0003",
              "sku_packing_length": 50,
              "sku_packing_width": 50,
              "sku_packing_height": 50,
              "sku_packing_volume": 125000,
              "sku_packing_weight": 3000,
              "sku_packing_amount": 60
            }
          }
        ]
      }
    ]
  }
}`;

const Sku_Sync = ({ isOpen, closeModal }) => {
  const [code, setCode] = useState(defaultJson);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) return;
    // Reset error message when modal opens
    setError(null);
  }, [isOpen]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const parsed = JSON.parse(code); // Attempt to parse the JSON
  
      // Send the data to the FastAPI backend using fetch
      const response = await fetch("http://localhost:8000/save-sku/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parsed),
      });
  
      if (response.ok) {
        alert("✅ JSON saved!");
        closeModal();  // Close the modal after successful save
      } else {
        alert("❌ Failed to save SKU data!");
      }
    } catch (err) {
      setError("❌ Invalid JSON format! Please check the format of your input.");
      console.error("JSON Parse Error: ", err);  // Log the error for debugging
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>SKU Sync Editor</h2>
        <Editor
          value={code}
          onValueChange={setCode}
          padding={10}
          highlight={(code) => code} // No syntax highlighting
        />
        {error && <div className="error-message" style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
        <div className="modal-buttons" style={{ marginTop: '10px' }}>
          <button onClick={handleSave} disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save'}
          </button>
          <button onClick={closeModal} style={{ marginLeft: '10px' }}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default Sku_Sync;
