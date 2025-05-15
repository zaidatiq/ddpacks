import React from 'react';
import { Container, Button, Row, Col, Card } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const navigate = useNavigate();

  return (
    <Container className="mt-5">
      <h2 className="text-center mb-4">Admin Panel</h2>
      <Row className="g-4">
        <Col md={4}>
          <Card className="text-center p-3 shadow">
            <Card.Body>
              <Card.Title>Track Inventory</Card.Title>
              <Button variant="primary" onClick={() => navigate('/admin/inventory')}>
                View Inventory
              </Button>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="text-center p-3 shadow">
            <Card.Body>
              <Card.Title>Manage SKUs</Card.Title>
              <Button variant="secondary" onClick={() => navigate('/admin/skus')}>
                Add New SKU
              </Button>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="text-center p-3 shadow">
            <Card.Body>
              <Card.Title>Add Inventory</Card.Title>
              <Button variant="success" onClick={() => navigate('/admin/add-inventory')}>
                Add Inventory
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AdminDashboard;
