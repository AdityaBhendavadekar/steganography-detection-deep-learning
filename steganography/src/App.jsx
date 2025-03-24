import { useState } from "react";

export default function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    setImage(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleUpload = async () => {
    if (!image) {
      alert("Please select an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", image);

    setLoading(true);
    setResult("");

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data.prediction);
    } catch (error) {
      console.error("Error:", error);
      setResult("Error detecting steganography.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center text-white relative"
      style={{
        backgroundImage: "url('https://wallpaperaccess.com/full/1867010.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      {/* Overlay for better readability */}
      <div className="absolute inset-0 bg-black opacity-50"></div>

      {/* Navbar */}
      <nav className="w-full bg-black/70 shadow-lg py-4 text-center text-lg font-semibold uppercase tracking-widest relative z-10 border-b border-green-500">
        🛡️ Cyber Security - Steganography Detection 🛡️
      </nav>

      <br /><br />
      <br />

      {/* Upload Box */}
      <div className="relative z-10 bg-white/10 border border-green-500 shadow-lg p-8 rounded-xl w-96 text-center backdrop-blur-md">
        <h2 className="text-lg font-semibold text-green-400 mb-4">
          Click here to Upload
        </h2>
        <label className="block bg-gray-800/50 text-white font-bold py-5 rounded-lg hover:bg-gray-700 transition cursor-pointer">
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="hidden"
          />
          {preview ? (
            <img
              src={preview}
              alt="Uploaded"
              className="w-full h-48 object-cover rounded-lg border border-green-400 mx-auto"
            />
          ) : (
            "Click to Select an Image"
          )}
        </label>
      </div>

      {/* Detect Button */}
      <button
        onClick={handleUpload}
        className="mt-5 bg-blue-500 text-white font-bold px-6 py-2 rounded-lg hover:bg-blue-600 transition disabled:opacity-50 relative z-10"
        disabled={loading}
      >
        {loading ? "Detecting..." : "Detect Stegano"}
      </button>

      {/* Result Box */}
      {result && (
        <div className="mt-6 bg-black/70 text-green-400 font-mono p-4 rounded-lg border border-green-500 w-96 text-center relative z-10 backdrop-blur-md">
          <p className="text-lg">🛡️ Detection Result: {result}</p>
        </div>
      )}
    </div>
  );
}
