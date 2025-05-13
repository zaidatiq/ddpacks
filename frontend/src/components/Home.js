import React, { useEffect, useState } from 'react';
import api from '../api';
import { Card, Container, Row, Col } from 'react-bootstrap';
import NavigationBar from './Navbar';
import Footer from './Footer';
import './Home.css';  // optional for extra styling

const Home = () => {
  const [skus, setSkus] = useState([]);

  useEffect(() => {
    api.get('skus/')
      .then((response) => setSkus(response.data))
      .catch((error) => console.error(error));
  }, []);

  return (
    <>
      <NavigationBar />
      <Container className="mt-5">
        <h2 className="text-center mb-4 text-primary">Available Products</h2>
        <Row xs={1} md={3} className="g-4">
          {skus.map((sku, index) => (
            <Col key={index}>
              <Card className="h-100 shadow-sm product-card">
                <Card.Img
                  variant="top"
                  src="https://via.placeholder.com/300x200.png?text=Product+Image"
                  alt={sku.name}
                />
                <Card.Body>
                  <Card.Title>{sku.name}</Card.Title>
                  <Card.Text>{sku.description}</Card.Text>
                  <Card.Text>
                    <small className="text-muted">Case Config: {sku.case_config}</small>
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </Container>
      <Footer />
    </>
  );
};

export default Home;
