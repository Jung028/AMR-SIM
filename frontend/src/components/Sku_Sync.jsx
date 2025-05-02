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
        "sku_name": "adult_shoe",
        "sku_price": 18.9,
        "unit": "EACH",
        "remark": "Size US 10",
        "dimensions": {
          "sku_length": 30.0,
          "sku_width": 11.0,
          "sku_height": 10.0,
          "sku_volume": 3300.0
        },
        "weight": {
          "sku_net_weight": 800,
          "sku_gross_weight": 1000
        },
        "stock_limits": {
          "sku_min_count": 100,
          "sku_max_count": 20000
        },
        "sku_shelf_life": 365,
        "sku_specification": "1pair/box",
        "sku_status": 1,
        "sku_abc": "A",
        "is_sequence_sku": 0,
        "sku_production_location": "Beijing",
        "sku_brand": "Generic",
        "sku_attributes": {
          "sku_size": "US10",
          "sku_color": "black",
          "sku_style": "sneaker"
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
            "sku_packing_spec": "1*6*10",
            "primary": {
              "sku_packing_code": "code1",
              "sku_packing_length": 33,
              "sku_packing_width": 13,
              "sku_packing_height": 12,
              "sku_packing_volume": 5148,
              "sku_packing_weight": 1100,
              "sku_packing_amount": 1
            },
            "secondary": {
              "sku_packing_code": "PM0002",
              "sku_packing_length": 70,
              "sku_packing_width": 42,
              "sku_packing_height": 25,
              "sku_packing_volume": 73500,
              "sku_packing_weight": 7000,
              "sku_packing_amount": 6
            },
            "tertiary": {
              "sku_packing_code": "PL0003",
              "sku_packing_length": 100,
              "sku_packing_width": 80,
              "sku_packing_height": 60,
              "sku_packing_volume": 480000,
              "sku_packing_weight": 25000,
              "sku_packing_amount": 60
            }
          }
        ]
      }
    ]
  }
}
`;

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
    setError(null);
    console.log("🔍 Attempting to save JSON");
  
    try {
      const parsed = JSON.parse(code);
      console.log("✅ Parsed JSON:", parsed);
  
      const response = await fetch("http://localhost:8000/save-sku/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parsed),
      });
  
      const text = await response.text(); // Even on error, get the full body
      console.log("📥 Server response text:", text);
  
      if (!response.ok) {
        setError(`❌ Server returned ${response.status}: ${text}`);
        console.error("❌ Bad Request - Backend rejected payload", {
          status: response.status,
          body: parsed,
        });
      } else {
        alert("✅ JSON saved successfully!");
        closeModal();
      }
    } catch (err) {
      setError("❌ Invalid JSON or server error. See console for details.");
      console.error("❌ Exception caught:", err);
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
