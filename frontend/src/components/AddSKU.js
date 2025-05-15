import React, { useState } from 'react';
import api from '../api';
import { Form, Button, Container, Alert } from 'react-bootstrap';

const AddSKU = () => {
  const [formData, setFormData] = useState({
    sku_code: '',
    name: '',
    description: '',
    unit_of_measurement: '',
    units_per_packet: '',
  });

  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('skus/', formData);
      setMessage({ type: 'success', text: res.data.message });
      setFormData({
        sku_code: '',
        name: '',
        description: '',
        unit_of_measurement: '',
        units_per_packet: '',
      });
    } catch (err) {
      setMessage({ type: 'danger', text: err.response?.data?.error || 'Something went wrong' });
    }
  };

  return (
    <Container className="mt-4">
      <h2>Add New SKU</h2>
      {message && <Alert variant={message.type}>{message.text}</Alert>}
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>SKU Code</Form.Label>
          <Form.Control type="text" name="sku_code" value={formData.sku_code} onChange={handleChange} required />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Name</Form.Label>
          <Form.Control type="text" name="name" value={formData.name} onChange={handleChange} required />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Description</Form.Label>
          <Form.Control type="text" name="description" value={formData.description} onChange={handleChange} />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Unit of Measurement</Form.Label>
          <Form.Control type="text" name="unit_of_measurement" value={formData.unit_of_measurement} onChange={handleChange} />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Units per Packet</Form.Label>
          <Form.Control type="number" name="units_per_packet" value={formData.units_per_packet} onChange={handleChange} />
        </Form.Group>
        <Button type="submit" variant="primary">Add SKU</Button>
      </Form>
    </Container>
  );
};

export default AddSKU;
