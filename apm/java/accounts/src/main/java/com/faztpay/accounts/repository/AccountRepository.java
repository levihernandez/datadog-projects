package com.faztpay.accounts.repository;

import com.faztpay.accounts.model.AccountModel;

import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface AccountRepository extends JpaRepository<AccountModel, UUID> {
}
