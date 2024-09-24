package com.faztpay.accounts.model;

import java.math.BigDecimal;
import java.sql.Timestamp;
import java.util.UUID;

import jakarta.persistence.*;

@Entity
@Table(name = "accounts") // Specify the correct table name here
public class AccountModel {
    @Id
    @GeneratedValue
    private UUID id;  // Primary key

    @Column(nullable = false, unique = true)
    private String username;  // Username field

    @Column(nullable = false)
    private BigDecimal balance;    // Balance field

    @Column(name = "created_at", nullable = false)
    private Timestamp createdAt;  // Creation timestamp

    @Column(name = "updated_at", nullable = false)
    private Timestamp updatedAt;  // Update timestamp

    // Getters and Setters

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public BigDecimal getBalance() {
        return balance;
    }

    public void setBalance(BigDecimal balance) {
        this.balance = balance;
    }

    public Timestamp getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Timestamp createdAt) {
        this.createdAt = createdAt;
    }

    public Timestamp getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Timestamp updatedAt) {
        this.updatedAt = updatedAt;
    }
}
