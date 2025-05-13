import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import AdminDashboard from './components/AdminDashboard';
import InventoryPage from './components/InventoryPage';
import AddSKU from './components/AddSKU';
import AddInventory from './components/AddInventory';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/inventory" element={<InventoryPage />} />
        <Route path="/admin/add-sku" element={<AddSKU />} />
        <Route path="/admin/add-inventory" element={<AddInventory />} />
      </Routes>
    </Router>
  );
}

export default App;
