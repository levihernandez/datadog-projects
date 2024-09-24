package com.faztpay.accounts.controller;

import com.faztpay.accounts.model.AccountModel;
import com.faztpay.accounts.repository.AccountRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.transaction.Transactional;

import java.math.BigDecimal;
import java.util.UUID;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    @Autowired
    private AccountRepository accountRepository;

    @PostMapping("/submit")
    @Transactional
    public ResponseEntity<String> submitPayment(@RequestParam UUID accountId, @RequestParam String username, @RequestParam BigDecimal amount) {
        AccountModel account = accountRepository.findById(accountId).orElse(null);
        if (account == null || !account.getUsername().equals(username)) {
            return ResponseEntity.badRequest().body("Account not found or user not authorized");
        }

        //account.addAmount();
        account.setBalance(account.getBalance().add(amount));
        accountRepository.save(account);
        return ResponseEntity.ok("Payment submitted successfully");
    }

    @PostMapping("/withdraw")
    @Transactional
    public ResponseEntity<String> withdrawMoney(@RequestParam UUID accountId, @RequestParam String username, @RequestParam BigDecimal amount) {
        // Check the account exists
        AccountModel account = accountRepository.findById(accountId).orElse(null);
        if (account == null) {
            return ResponseEntity.badRequest().body("Account not found");
        }
        if (!account.getUsername().equals(username)) {
            return ResponseEntity.badRequest().body("Username does not match");
        }
        if (account.getBalance().compareTo(amount) < 0) {
            return ResponseEntity.badRequest().body("Insufficient funds");
        }
        account.setBalance(account.getBalance().subtract(amount));
        accountRepository.save(account);
        return ResponseEntity.ok("Withdrawal successful");
    }

}
